"""
MESTRE ESP-NOW (MicroPython) - casa autônoma

Controla os três receptores:
  - receptor_cozinha_c3.py          -> local 'cozinha'
  - receptor_quarto_dormir_c3.py    -> local 'quarto_dormir'
  - receptor_quarto_banheiro_c3.py  -> local 'quarto_banheiro'
E também os equipamentos do PRÓPRIO mestre (luminária e ar condicionado/cooler),
acionados direto pelos pinos, sem ESP-NOW -> local 'mestre'

Uso no terminal (REPL / serial):
  <local> <equipamento> liga
  <local> <equipamento> desliga
  <local> ar vel <0-5>            (ventilação do ar condicionado)
  tudo desliga                    (desliga tudo, em todos os locais)
  lista | ajuda | fim

Exemplos:
  cozinha fogaoEl liga
  quarto_banheiro luminaria_q desliga
  quarto_dormir tela liga
  cozinha ar vel 3
  mestre luminaria liga
  mestre ar vel 3

Uso por outro código (sensores, Raspberry Pi, rotinas):
  controlar('cozinha', 'airfryer', 'ligar', True)
  controlar('quarto_dormir', 'ar condicionado', 'ventilacao', 3)
"""

from json import dumps
from time import sleep_ms
from machine import Pin, PWM
import network
import espnow

#######################################################################################################
# Wi-Fi (STA) + ESP-NOW
rede = network.WLAN(network.STA_IF)
rede.active(True)
rede.disconnect()          # ESP-NOW não precisa de roteador

prot = espnow.ESPNow()
prot.active(True)

print("MAC deste mestre:", rede.config('mac').hex())

#######################################################################################################
# MACs dos receptores (6 bytes reais).
# Cada receptor imprime o próprio MAC ao ligar ("MAC deste receptor: ...").
# Copie esse valor para cá, ex.: bytes.fromhex('aca704d69138')
BROADCAST = b'\xff\xff\xff\xff\xff\xff'

esp_cozinha         = bytes.fromhex('aca704d69138')  # ac:a7:04:d6:91:38  (confirmar)
esp_quarto_dormir   = bytes.fromhex('44bd8d25b054')  # 44:bd:8d:25:b0:54
esp_quarto_banheiro = bytes.fromhex('44bd8d249a6c')  # 44:bd:8d:24:9a:6c

#######################################################################################################
# Equipamentos do PRÓPRIO mestre (acionados direto pelos pinos, sem ESP-NOW)
# Ajuste os pinos para a sua placa (evite pinos de boot/strapping e de UART).
PINO_LUMINARIA = 4
PINO_COOLER    = 5       # use transistor/MOSFET; não ligue o cooler direto no pino
FREQ_COOLER    = 1000    # Hz do PWM do cooler

luminaria_local = Pin(PINO_LUMINARIA, Pin.OUT, value=0)
cooler_local    = PWM(Pin(PINO_COOLER), freq=FREQ_COOLER, duty_u16=0)   # começa desligado

#######################################################################################################
# Tabela de locais -> (MAC do receptor, equipamentos que ESSE receptor aceita)
# MAC = None significa equipamento do próprio mestre (executado localmente, sem ESP-NOW)
# Os nomes dos equipamentos são exatamente os que cada receptor_*.py tem em "pinos"
# (mais o "ar condicionado", tratado à parte em cada receptor).
LOCAIS = {
    'cozinha': (esp_cozinha,
                ['luminaria_cgg', 'fogaoEl', 'airfryer', 'microondas',
                 'ar condicionado']),

    'quarto_dormir': (esp_quarto_dormir,
                      ['luminaria', 'abajur', 'tela',
                       'ar condicionado']),

    'quarto_banheiro': (esp_quarto_banheiro,
                        ['luminaria_q', 'luminaria_b', 'janela_motor', 'abajur',
                         'ar condicionado']),

    'mestre': (None,
               ['luminaria', 'ar condicionado']),
}

NIVEL_MAX = 5          # os receptores aceitam ventilação de 0 a 5
TENTATIVAS = 3         # reenvios se o receptor não confirmar

# Registra todos os receptores como peers (antes de qualquer send)
for _local, (_mac, _eq) in LOCAIS.items():
    if _mac is None:
        continue       # equipamento do próprio mestre (sem ESP-NOW)
    try:
        prot.add_peer(_mac)
    except OSError:
        pass           # já registrado (ex.: dois locais com o mesmo MAC provisório)

#######################################################################################################
# Funções

def _resolver_equipamento(local, nome):
    """Devolve o nome exato do equipamento naquele local (ou None)."""
    nome = nome.strip().lower()
    if nome in ('ar', 'ar_condicionado'):
        nome = 'ar condicionado'
    for eq in LOCAIS[local][1]:
        if eq.lower() == nome:
            return eq
    return None


def _enviar(mac, comando):
    """Envia o JSON e repete se o receptor não confirmar. True = confirmado."""
    if mac == BROADCAST:
        print("  MAC desse receptor ainda não foi definido; comando não enviado.")
        return False

    texto = dumps(comando)
    for _ in range(TENTATIVAS):
        try:
            if prot.send(mac, texto):
                return True
        except OSError as erro:
            print("  Erro ao enviar:", erro)
        sleep_ms(50)
    return False


_nivel_cooler = NIVEL_MAX      # último nível de ventilação do cooler do mestre


def _duty(nivel):
    """Nível 0-5 -> duty do PWM (0-65535)."""
    return nivel * 65535 // NIVEL_MAX


def _executar_local(eq, acao, parametro):
    """Executa direto nos pinos do mestre (sem ESP-NOW). True = executado."""
    global _nivel_cooler

    if eq == 'luminaria':
        luminaria_local.value(1 if parametro else 0)
        return True

    if eq == 'ar condicionado':
        if acao == 'ligar':
            # ligar volta ao último nível usado; desligar zera o PWM
            cooler_local.duty_u16(_duty(_nivel_cooler) if parametro else 0)
        else:  # ventilacao
            if parametro > 0:
                _nivel_cooler = parametro
            cooler_local.duty_u16(_duty(parametro))   # nível 0 = parado
        return True

    return False


def controlar(local, equipamento, acao, parametro):
    """
    Função principal: manda um comando para um receptor.
      local        -> 'cozinha' | 'quarto_dormir' | 'quarto_banheiro'
      equipamento  -> nome do equipamento naquele local
      acao         -> 'ligar' | 'ventilacao'
      parametro    -> True/False (ligar) ou 0-5 (ventilacao)
    Retorna True se o receptor confirmou o recebimento.
    """
    if local not in LOCAIS:
        print("Local desconhecido:", local)
        return False

    eq = _resolver_equipamento(local, equipamento)
    if eq is None:
        print("Equipamento '%s' não existe em %s." % (equipamento, local))
        return False

    if acao == 'ligar':
        parametro = bool(parametro)
    elif acao == 'ventilacao':
        if eq != 'ar condicionado':
            print("Ventilação só vale para o ar condicionado.")
            return False
        try:
            parametro = max(0, min(NIVEL_MAX, int(parametro)))
        except (TypeError, ValueError):
            print("Nível de ventilação inválido:", parametro)
            return False
    else:
        print("Ação desconhecida:", acao)
        return False

    comando = {'equipamento': eq, 'acao': acao, 'parametro': parametro}
    mac = LOCAIS[local][0]
    if mac is None:
        ok = _executar_local(eq, acao, parametro)    # local, sem ESP-NOW
    else:
        ok = _enviar(mac, comando)
    print(("OK  " if ok else "FALHA ") + local + " -> " + dumps(comando))
    return ok


def desligar_tudo():
    """Manda 'ligar: False' para todos os equipamentos de todos os locais."""
    for local, (_mac, equipamentos) in LOCAIS.items():
        for eq in equipamentos:
            controlar(local, eq, 'ligar', False)


def listar():
    for local, (mac, equipamentos) in LOCAIS.items():
        if mac is None:
            estado = "local, sem ESP-NOW"
        else:
            estado = "MAC definido" if mac != BROADCAST else "MAC A DEFINIR"
        print("%s [%s]: %s" % (local, estado, ", ".join(equipamentos)))


AJUDA = """
Comandos:
  <local> <equipamento> liga
  <local> <equipamento> desliga
  <local> ar vel <0-5>     (ventilacao do ar condicionado)
  tudo desliga             (desliga tudo, em todos os locais)
  lista | ajuda | fim

Locais: cozinha, quarto_dormir, quarto_banheiro, mestre (este próprio ESP)

Exemplos:
  cozinha fogaoEl liga
  quarto_banheiro luminaria_q desliga
  quarto_dormir tela liga
  cozinha ar vel 3
  mestre luminaria liga
  mestre ar vel 3
"""


def ajuda():
    print(AJUDA)

#######################################################################################################
# Loop de comandos (terminal)

def interpretar(linha):
    partes = linha.split()
    if not partes:
        return True

    p0 = partes[0].lower()

    if p0 == 'fim':
        return False
    if p0 == 'lista':
        listar()
    elif p0 == 'ajuda':
        ajuda()
    elif p0 == 'tudo' and len(partes) == 2 and partes[1].lower() == 'desliga':
        desligar_tudo()
    elif p0 in LOCAIS and len(partes) == 3 and partes[2].lower() in ('liga', 'desliga'):
        controlar(p0, partes[1], 'ligar', partes[2].lower() == 'liga')
    elif p0 in LOCAIS and len(partes) == 4 and partes[2].lower() == 'vel':
        controlar(p0, partes[1], 'ventilacao', partes[3])
    else:
        print('Comando inválido. Digite "ajuda".')
    return True


def main():
    listar()
    print('Digite "ajuda" para ver os comandos.')
    while True:
        if not interpretar(input('> ')):
            break
    print('Encerrado.')


if __name__ == '__main__':
    main()

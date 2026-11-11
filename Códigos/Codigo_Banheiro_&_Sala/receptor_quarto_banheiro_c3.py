"""
Receptor ESP-NOW (ESP32-C3 Super Mini + MicroPython) - QUARTO & BANHEIRO - 44:bd:8d:24:9a:6c

Comandos de exemplo (JSON que o emissor deve enviar):
{"equipamento":"abajur", "acao":"ligar", "parametro":true}
{"equipamento":"luminaria_q", "acao":"ligar", "parametro":true}
{"equipamento":"luminaria_b", "acao":"ligar", "parametro":true}
{"equipamento":"janela_motor", "acao":"ligar", "parametro":true}
{"equipamento":"janela_motor", "acao":"ligar", "parametro":false}
{"equipamento":"ar condicionado", "acao":"ligar", "parametro":true}
{"equipamento":"ar condicionado", "acao":"ligar", "parametro":false}
{"equipamento":"ar condicionado", "acao":"ventilacao", "parametro":3}   # nível 0 a 5
"""

from json import loads
from time import sleep_ms
from machine import Pin
from neopixel import NeoPixel
import network
import espnow
# dependendo do motor, importar aqui as bibliotecas necessárias

#######################################################################################################
# Equipamentos (cada um é um pino de saída, começando desligado)
# Pinos do ESP32-C3 Super Mini: evita GPIO 2, 8 e 9 (strapping/LED/BOOT) e 20/21 (UART)
pinos = {
    "luminaria_q":  Pin(0, Pin.OUT, value=0),
    "luminaria_b":  Pin(1, Pin.OUT, value=0),
    "janela_motor": Pin(3, Pin.OUT, value=0),
    "abajur":       Pin(4, Pin.OUT, value=0),
}

# Faz de conta que é o ar condicionado (6 LEDs RGB)
NUM_LEDS = 6
arCondicionado = NeoPixel(Pin(5), NUM_LEDS)
cores = (
    (0, 0, 255),
    (0, 255, 255),
    (0, 255, 0),
    (255, 255, 0),
    (0, 0, 255),
    (255, 0, 0),
)

#######################################################################################################
# ESP-NOW: precisa do Wi-Fi ligado, mas sem conectar em roteador
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()

e = espnow.ESPNow()
e.active(True)

# Esse MAC é o endereço que o emissor usa para enviar mensagens para cá
print("MAC deste receptor (quarto & banheiro):", sta.config('mac').hex())

#######################################################################################################
# Funções auxiliares

def paraBool(valor):
    """Converte o parâmetro recebido em 0/1, aceitando bool, número ou texto."""
    if isinstance(valor, str):
        return 1 if valor.strip().lower() in ("true", "1", "on", "ligar") else 0
    return 1 if valor else 0


def apagarArCondicionado():
    for n in range(NUM_LEDS):
        arCondicionado[n] = (0, 0, 0)
    arCondicionado.write()


def ligarArCondicionado(acao, parametro=None):
    if acao == 'ligar':
        if paraBool(parametro):
            # acende os LEDs em branco, um a um
            for n in range(NUM_LEDS):
                arCondicionado[n] = (200, 200, 200)
                arCondicionado.write()
                sleep_ms(100)
        else:
            apagarArCondicionado()

    elif acao == 'ventilacao':
        # limita o nível entre 0 e 5 (evita IndexError)
        try:
            nivel = max(0, min(NUM_LEDS - 1, int(parametro)))
        except (TypeError, ValueError):
            print("Nível de ventilação inválido:", parametro)
            return

        apagarArCondicionado()
        # sobe do nível 0 até o nível pedido, acendendo mais LEDs a cada passo
        for n in range(nivel + 1):
            for j in range(n + 1):
                arCondicionado[j] = cores[n]
            arCondicionado.write()
            sleep_ms(200)

    else:
        print("Ação desconhecida para ar condicionado:", acao)


# Recebe um dicionário, ex: {"equipamento": "abajur", "acao": "ligar", "parametro": True}
def executarComando(comando):
    if not isinstance(comando, dict):
        print("Comando deve ser um objeto JSON:", comando)
        return

    equipamento = comando.get('equipamento')
    acao = comando.get('acao')
    parametro = comando.get('parametro')

    if equipamento in pinos:
        if acao == 'ligar':
            pinos[equipamento].value(paraBool(parametro))
        else:
            print("Ação desconhecida:", acao)

    elif equipamento == "ar condicionado":
        ligarArCondicionado(acao, parametro)

    else:
        print("Equipamento desconhecido:", equipamento)

#######################################################################################################
# Loop principal

print("Aguardando comandos ESP-NOW...")

while True:
    # recv(0) não espera: se não houver mensagem, devolve (None, None)
    mac, msg = e.recv(0)

    if msg:
        try:
            comando = loads(msg)        # texto JSON -> dicionário
            print("De:", mac.hex(), "->", comando)
            executarComando(comando)
        except Exception as erro:
            # JSON inválido ou erro no comando não trava o programa
            print("Mensagem inválida:", erro)

    sleep_ms(10)


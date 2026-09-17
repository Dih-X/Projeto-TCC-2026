from machine import Pin
from network import WLAN
from espnow import ESPNow
from json import loads
from time import sleep_ms


tela = Pin(4, Pin.OUT, value=0)


rede = WLAN(WLAN.IF_STA)
rede.active(True)


prot = ESPNow()
prot.active(True)


conteudo = ''
while conteudo is not None:
    for mac, msg in prot:
        try:
            conteudo = loads(msg.decode())
            if conteudo['equipamento'] == 'tela':
                if conteudo['acao'] == 'ligar':
                    tela.value(conteudo['parametro'])
            elif conteudo['equipamento'] == 'bum':
                conteudo = None
        except OSError as err:
            print("Erro de recepção:", err)
            sleep_ms(3000)

        except AttributeError as err:
            print(f"{mac}:{msg}")
            sleep_ms(3000)

        #{"equipamento":"tela", "acao":"ligar", "parametro":true}


'''
{"equipamento":"tela", "acao":"ligar", "parametro":true}
{"equipamento":"tela", "acao":"ligar", "parametro":false}
'''


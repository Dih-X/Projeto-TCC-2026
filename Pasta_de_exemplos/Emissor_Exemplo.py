from network import WLAN
from espnow import ESPNow
from json import dumps

rede = WLAN(WLAN.IF_STA)
rede.active(True)

prot = ESPNow()
prot.active(True)


destino = b'\xdc\x06\x75\x67\x61\x80'   # MAC address of peer's wifi interface
#dc:06:75:67:61:80
prot.add_peer(destino)      # Must add_peer() before send()

dicEquip = {'equipamento':'tela',
            'acao':'ligar',
            'parametro':True}

resposta = input('Liga/Desliga? ')

while resposta != 'Fim':
    r = resposta.lower().strip()
    if r == 'liga':
        dicEquip['parametro'] = True
    elif r == 'desliga':
        dicEquip['parametro'] = False
        
    conteudo = dumps(dicEquip)    
    prot.send(destino, conteudo)
    
    resposta = input('Liga/Desliga? ')

    

'''
{"equipamento":"tela", "acao":"ligar", "parametro":true}
{"equipamento":"tela", "acao":"ligar", "parametro":false}
'''


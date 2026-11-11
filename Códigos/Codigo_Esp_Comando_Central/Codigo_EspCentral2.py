from network import WLAN
from espnow import ESPNow
from json import dumps

rede = WLAN(WLAN.IF_STA)
rede.active(True)

prot = ESPNow()
prot.active(True)

#destino = b'\xdc\x06\x75\x67\x61\x80'   # MAC address of peer's wifi interface
#dc:06:75:67:61:80

esp_cozinhaAberta  = b'\xff\xff\xff\xff\xff\xff' #MAC endereco 1 - a definir
esp_quartoBanheiro = b'\xff\xff\xff\xff\xff\xff' #MAC endereco 2 - a definir
esp_quartoDormir   = b'\xff\xff\xff\xff\xff\xff' #MAC endereco 3 - a definir

prot.add_peer(destino)      # Must add_peer() before send()

'''
dicEquip = {'equipamento' : 'tela',
            'acao'        : 'ligar',
            'parametro'   : True}
'''

#----------------EspMini_Cozinha----------------

altFogao = {'equipamento' : 'fogaoEl',
            'acao'        : 'ligar',
            'parametro'   : False}

'''
altFogao = {'equipamento' : 'fogaoEl',
            'acao'        : 'ligar',
            'parametro'   : False}'''

#- - - - - - - - - - - - - - - - - - - - - - - -

altAirfryer = {'equipamento' : 'airfryer',
               'acao'        : 'ligar',
               'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altMicro = {'equipamento' : 'microondas',
            'acao'        : 'ligar',
            'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altLumcg = {'equipamento' : 'luminaria_cgg',
            'acao'        : 'ligar',
            'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altARcon = {'equipamento' : 'ar condicionado',
            'acao'        : 'ligar',
            'parametro'   : False}

altACven = {'equipamento' : 'ar condicionado',
            'acao'        : 'ventilacao',
            'parametro'   : 3} #velocidade - pode botar outros fatores como temperatura etc

#-----------------------------------------------
#-------------EspMini_QuartoBanheiro------------

altAbaju = {'equipamento' : 'abajur',
            'acao'        : 'ligar',
            'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altLumQu = {'equipamento' : 'luminaria_q',
            'acao'        : 'ligar',
            'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altLumBa = {'equipamento' : 'luminaria_b',
            'acao'        : 'ligar',
            'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altJanMo = {'equipamento' : 'janela_motor',
            'acao'        : 'ligar',
            'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altARcun = {'equipamento' : 'ar condicionado',
            'acao'        : 'ligar',
            'parametro'   : False}

altACvun = {'equipamento' : 'ar condicionado',
            'acao'        : 'ventilacao',
            'parametro'   : 3}

#-----------------------------------------------
#--------------EspMini_QuartoDormir-------------

altTelaPC = {'equipamento' : 'tela',
             'acao'        : 'ligar',
             'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altAbajuD = {'equipamento' : 'abajur',
             'acao'        : 'ligar',
             'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altLumDor = {'equipamento' : 'luminaria',
             'acao'        : 'ligar',
             'parametro'   : False}

#- - - - - - - - - - - - - - - - - - - - - - - -

altACquar = {'equipamento' : 'ar condicionado',
             'acao'        : 'ligar',
             'parametro'   : False}

altACvenQ = {'equipamento' : 'ar condicionado',
             'acao'        : 'ventilacao',
             'parametro'   : 3}

#-----------------------------------------------

#comandosCozinha
'''
{"equipamento":"fogaoEl", "acao":"ligar", "parametro":true}
{"equipamento":"fogaoEl", "acao":"ligar", "parametro":false}

{"equipamento":"airfryer", "acao":"ligar", "parametro":true}
{"equipamento":"airfryer", "acao":"ligar", "parametro":false}

{"equipamento":"microondas", "acao":"ligar", "parametro":true}
{"equipamento":"microondas", "acao":"ligar", "parametro":false}

{"equipamento":"luminaria_cgg", "acao":"ligar", "parametro":true}
{"equipamento":"luminaria_cgg", "acao":"ligar", "parametro":false}

{"equipamento":"ar condicionado", "acao":"ligar", "parametro":true}
{"equipamento":"ar condicionado", "acao":"ligar", "parametro":false}
{"equipamento":"ar condicionado", "acao":"ventilacao", "parametro":3}
'''

#comandosQuartoBanheiro
'''
{"equipamento":"abajur", "acao":"ligar", "parametro":true}
{"equipamento":"abajur", "acao":"ligar", "parametro":false}

{"equipamento":"luminaria_q", "acao":"ligar", "parametro":true}
{"equipamento":"luminaria_q", "acao":"ligar", "parametro":false}

{"equipamento":"luminaria_b", "acao":"ligar", "parametro":true}
{"equipamento":"luminaria_b", "acao":"ligar", "parametro":false}

{"equipamento":"janela_motor", "acao":"ligar", "parametro":true}
{"equipamento":"janela_motor", "acao":"ligar", "parametro":false}

{"equipamento":"ar condicionado", "acao":"ligar", "parametro":true}
{"equipamento":"ar condicionado", "acao":"ligar", "parametro":false}
{"equipamento":"ar condicionado", "acao":"ventilacao", "parametro":3}
'''

#comandosQuartoDormir
'''
{"equipamento":"tela", "acao":"ligar", "parametro":true}
{"equipamento":"tela", "acao":"ligar", "parametro":false}

{"equipamento":"abajur", "acao":"ligar", "parametro":true}
{"equipamento":"abajur", "acao":"ligar", "parametro":false}

{"equipamento":"luminaria", "acao":"ligar", "parametro":true}
{"equipamento":"luminaria", "acao":"ligar", "parametro":false}

{"equipamento":"ar condicionado", "acao":"ligar", "parametro":true}
{"equipamento":"ar condicionado", "acao":"ligar", "parametro":false}
{"equipamento":"ar condicionado", "acao":"ventilacao", "parametro":3}
'''

#-----------------------------------------------
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

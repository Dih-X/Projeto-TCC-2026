from json import loads
from time import sleep_ms
from machine import Pin
from neopixel import NeoPixel
#dependendo do motor, exportar bibliotecas necessarias

luminaria_cgg = Pin(23, Pin.OUT, value=0)

fogaoEl = Pin(21, Pin.OUT, value=0)
airfryer = Pin(27, Pin.OUT, value=0)
microondas = Pin(22, Pin.OUT, value=0)

botMsg = Pin(26, Pin.IN, Pin.PULL_DOWN)

# Faz de conta que é o ar condicionado
arCondicionado = NeoPixel(Pin(25),6)
cores = ((0,0,255),
         (0,255,255),
         (0,255,0),
         (255,255,0),
         (0,0,255),
         (255,0,0)
         )

#######################################################################################################

def ligarArCondicionado(acao, parametro=None):
    global arCondicionado

    if acao == 'ligar':
        if parametro == True:
            for n in range(6):
                arCondicionado[n] = (200,200,200)
                arCondicionado.write()
                sleep_ms(100)
        else:
            for n in range(6):
                arCondicionado[n] = (0,0,0)
            arCondicionado.write()
            sleep_ms(10)

    elif acao == 'ventilacao':
        for n in range(6):
            arCondicionado[n] = (0,0,0)
            arCondicionado.write()
            sleep_ms(10)
        for n in range(parametro+1):
            for j in range(n+1):
                arCondicionado[j] = cores[n]
            arCondicionado.write()
            sleep_ms(200)

#######################################################################################################

ba = botMsg.value()

while True:
    bt = botMsg.value()
    if bt != ba:
        if bt == 1:

            msg = input('Comando: ')
            comando = loads(msg)

            if comando['equipamento'] == "microondas":
                if comando['acao'] == 'ligar':
                    microondas.value(comando['parametro'])

            elif comando['equipamento'] == "luminaria_cgg":
                print ('Coisas de luminária')
                
                if comando['acao'] == 'ligar':
                    luminaria_cgg.value(comando['parametro'])
                
            elif comando['equipamento'] == "ar condicionado":
                ligarArCondicionado(comando['acao'], comando['parametro'])

                print ('Coisas de ar condicionado')

            elif comando['equipamento'] == "fogaoEl":
                print ('Coisas de luminária no banheiro')
                
                if comando['acao'] == 'ligar':
                    fogaoEl.value(comando['parametro'])

            elif comando['equipamento'] == "airfryer":
                print ('Coisas de luminária no banheiro')
                
                if comando['acao'] == 'ligar':
                    airfryer.value(comando['parametro'])      

        ba = bt
        sleep_ms(100)

#######################################################################################################
#Comandos_de_exemplo:
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
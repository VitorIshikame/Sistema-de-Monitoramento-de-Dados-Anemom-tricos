from math import radians, degrees, sin, cos, atan2
from time import ticks_us, ticks_ms, localtime
from machine import Pin, ADC


def windVane (pino, periodoUs, tempoAmostraUs):
x = ADC(Pin(pino))
x.atten(ADC.ATTN_11DB)
direcoes = []
angs = []
soma = [0,0]
a = ticks_us()
tempo = 0
total = 0
media = 0
while ticks_us() <= a + periodoUs:
    if ticks_us() >= tempo:
        dir = x.read()
        graus = ((dir)*(360)/4095)
        tempo = ticks_us() + tempoAmostraUs
        direcoes.append(graus)
for i in range(len(direcoes)):
    angs.append((sin(radians(direcoes[i])),cos(radians(direcoes[i]))))
for i in range(len(angs)):
    soma[0] += angs[i][0]
    soma[1] += angs[i][1]
media = round(degrees(atan2(soma[0],soma[1])))
return(media)

def windVane1 (pino):
    x = ADC(Pin(pino))
    x.atten(ADC.ATTN_11DB)
    dir = x.read()
    graus = ((dir)*(360)/4095)
    return(graus)

def anemometro (pino, periodoUs):
    x = Pin(pino, Pin.IN, Pin.PULL_DOWN)
    a = ticks_us()
    xAnt = 0
    qPulsos = 0
    vel = 0
    while ticks_us() <= a + periodoUs:
        if x.value() != xAnt and x.value() == 1:
            xAnt = x.value()
            qPulsos += 1
        elif x.value() != xAnt and x.value() == 0:
            xAnt = x.value()
    if qPulsos == 0:
        vel = 0
    else:
        vel = round((0.051*qPulsos)/(periodoUs/1000000), 1)
    return vel

def anemometro3 (pino1, pino2, pino3, periodoUs):
    x = Pin(pino1, Pin.IN, Pin.PULL_DOWN)
    y = Pin(pino2, Pin.IN, Pin.PULL_DOWN)
    z = Pin(pino3, Pin.IN, Pin.PULL_DOWN)
    a = ticks_us()
    xAnt = 0
    yAnt = 0
    zAnt = 0
    xPulsos = 0
    yPulsos = 0
    zPulsos = 0
    xVel = 0
    yVel = 0
    zVel = 0
    while ticks_us() <= a + periodoUs:
        if x.value() != xAnt and x.value() == 1:
            xAnt = x.value()
            xPulsos += 1
        elif x.value() != xAnt and x.value() == 0:
            xAnt = x.value()
        if y.value() != yAnt and y.value() == 1:
            yAnt = y.value()
            yPulsos += 1
        elif y.value() != yAnt and y.value() == 0:
            yAnt = y.value()
        if z.value() != zAnt and z.value() == 1:
            zAnt = z.value()
            zPulsos += 1
        elif z.value() != zAnt and z.value() == 0:
            zAnt = z.value()
    if xPulsos == 0:
        xVel = 0
    else:
        xVel = round((0.051*xPulsos)/(periodoUs/1000000), 1)
    if yPulsos == 0:
        yVel = 0
    else:
        yVel = round((0.051*yPulsos)/(periodoUs/1000000), 1)
    if zPulsos == 0:
        zVel = 0
    else:
        zVel = round((0.051*zPulsos)/(periodoUs/1000000), 1)
    return xVel,yVel,zVel

def dataHora():
    data = []
    hora = []
    dataHora = []
    for i in range(3):
        data.append(str(localtime()[i]))
        dataStr = '-'.join(data)
    dataHora.append(dataStr)
    for i in range(3,6):
        hora.append(str(localtime()[i]))
        horaStr = '-'.join(hora)
    dataHora.append(horaStr)
    local = '-'.join(dataHora)
    return local

def arq(t,x,y,z):
    dados = [str(x),str(y),str(z)]
    planilha = []
    csv = ';'.join(dados)
    a = ticks_us()
    g = 0
    while ticks_us() >= a + 1000000:
        if g < t*60:
            planilha.append(csv)
            g += 1
        else:
            with open (f'{z}.csv', 'w') as gravar:
                gravar.write('Velocidade;Direção;Data/Hora')
                gravar.write('\n')
                for i in planilha:
                    gravar.write(i)
                    gravar.write('\n')
                print(f'{z}.csv foi gravado')
            

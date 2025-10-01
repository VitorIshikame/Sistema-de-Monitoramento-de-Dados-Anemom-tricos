from time import ticks_ms, sleep, localtime
from ulora import LoRa, ModemConfig, SPIConfig
from funcoesBolsa import dataHora
from network import WLAN, STA_IF
from umqtt.simple import MQTTClient
from json import dumps, loads
import ntptime
from machine import Timer, reset, Pin

def conectaWifi(rede, senha):
    wifi = WLAN(STA_IF)
    wifi.active(True)
    while not wifi.isconnected():
        try:
            wifi.connect(rede, senha)
        except:
            sleep(1)
    print('conectado!')
    return wifi if wifi.isconnected else None

def msg(payload):
    global mssg
    mssg = payload.message.decode()

def desligaTudo(timer):
        reset()

RFM95_RST = 14
RFM95_SPIBUS = SPIConfig.esp32_2
RFM95_CS = 5
RFM95_INT = 26
RF95_FREQ = 915.0
RF95_POW = 20
CLIENT_ADDRESS = 1
SERVER_ADDRESS = 2

rede = '' #Preencher de acordo
senha = '' #Preencher de acordo
mssg = ''
payload = ''
ticksLoc= 0
tempoMqtt = 0

net = conectaWifi(rede,senha)

ntptime.settime()

timer = Timer(1)
timer.init(mode=Timer.ONE_SHOT, period=300000, callback=desligaTudo)

lora = LoRa(RFM95_SPIBUS,
            RFM95_INT,
            SERVER_ADDRESS,
            RFM95_CS,
            reset_pin=RFM95_RST,
            freq=RF95_FREQ,
            tx_power=RF95_POW,
            acks=True)

topico = b'v1/devices/me/telemetry'
cliente = MQTTClient('0d8d0be0-61f3-11f0-8543-cf220f4e0102',
                     'demo.thingsboard.io',
                     user = 'lehb4ik59kt5h5kicuy6',
                     password = '')
cliente.connect()

lora.on_recv = msg
lora.set_mode_rx()

while True:
  
    #sincronização para definir data e hora
    if mssg == 'locReq':
        if ticks_ms() >= ticksLoc:
            lora.send_to_wait('loctime',CLIENT_ADDRESS)
            ticksLoc = ticks_ms() + 5000
    if mssg == 'loctime1':
        if ticks_ms() >= ticksLoc:
            lora.send_to_wait(f'localtime2;{dataHora()}',CLIENT_ADDRESS)
            ticksLoc = ticks_ms() + 5000
    if mssg == 'loctimeOk':
        if ticks_ms() >= ticksLoc:
            lora.send_to_wait('manda',CLIENT_ADDRESS)
            ticksLoc = ticks_ms() + 5000
    
    #Recebe dados e envia pra nuvem
    if mssg != '' and mssg.strip('0123456789-;\n.')[0] == ('@'):
        if ticks_ms() >= tempoMqtt:
            dicDados = {"Vel1":mssg.split(';')[1],
                        "Vel2":mssg.split(';')[2],
                        "Vel3":mssg.split(';')[3],
                        "Dir":mssg.split(';')[4],
                        "Temp":mssg.split(';')[5],
                        "Pressao":mssg.split(';')[6]}
            payload = dumps(dicDados).encode()
            cliente.publish(topico,payload)
            tempoMqtt = ticks_ms() + 5000

cliente.disconnect()


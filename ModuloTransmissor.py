from time import ticks_ms, sleep
from ulora import LoRa, ModemConfig, SPIConfig
from machine import RTC, Pin, I2C, Timer, reset, SPI
from funcoesBolsa import anemometro3, windVane1
import onewire
import ds18x20
import BME280
import sdcard
import os

try:
    
    def msg(payload):
        global mssg
        mssg = payload.message.decode()
      
    def desligaTudo(timer):
        reset()
      
    def grava(timerSD):
        global listaGrava
        try:
            spi=SPI(2)
            sd=sdcard.SDCard(spi,Pin(15))
            vfs=os.VfsFat(sd)
            os.mount(sd,'/sd')
            gravaDados = '\n'.join(listaGrava)
            with open ("/sd/dados.csv","a") as arq:
                arq.write(f'\n{gravaDados}')
        except:
            grava()

    RFM95_RST = 14
    RFM95_SPIBUS = SPIConfig.esp32_2
    RFM95_CS = 5
    RFM95_INT = 26
    RF95_FREQ = 915.0
    RF95_POW = 20
    CLIENT_ADDRESS = 1
    SERVER_ADDRESS = 2
    
    ds = Pin(33)
    ds18 = ds18x20.DS18X20(onewire.OneWire(ds))
    roms = ds18.scan()
    i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
    bmp = BME280.BME280(i2c=i2c)
    timer = Timer(1)
    timer.init(mode=Timer.ONE_SHOT, period=300000, callback=desligaTudo)
    timerSD = Timer(2)
    timerSD.init(mode=Timer.ONE_SHOT, period=295000, callback=grava)
    
    mssg = ''
    locOk = 0
    tempoDados = 20000
    datetime = []
    l = [[],[],[],[],[],[],[],[],[]]
    pacote = [[]]
    listaGrava = []
    
    lora = LoRa(RFM95_SPIBUS,
                RFM95_INT,
                CLIENT_ADDRESS,
                RFM95_CS,
                reset_pin=RFM95_RST,
                freq=RF95_FREQ,
                tx_power=RF95_POW,
                acks=True)

    lora.on_recv = msg
    lora.set_mode_rx()
    
    rtc = RTC()
   
    while True:

    #Sincronização para definir data e hora
        if locOk == 0:
            lora.send_to_wait('locReq',SERVER_ADDRESS)
            sleep(3)
            if mssg == 'loctime':
                lora.send_to_wait('loctime1',SERVER_ADDRESS)
                sleep(3)
            if mssg.split(';')[0] == 'localtime2':
                try:
                    localTeste = mssg.split(';')[1]
                    lT2 = localTeste.split('-')
                    localTeste3 = '0'.join(lT2)
                    if isinstance(int(localTeste3),int) == True:
                        for i in range(6):
                            lT2[i] = int(lT2[i])
                        tuplaLocal = (lT2[0],lT2[1],lT2[2],0,lT2[3],lT2[4],lT2[5],0)
                        rtc.datetime(tuplaLocal)
                        lora.send_to_wait('loctimeOk',SERVER_ADDRESS)
                        locOk = 1
                        sleep(3)
                except:
                    lora.send_to_wait('loctime1',SERVER_ADDRESS)
                    sleep(3)    

        #Leitura e envio dos dados
        while mssg == 'manda':           
            vel = anemometro3(34,35,32,20000000)
            for i in range(7):
                if i != 3:
                    datetime.append(str('{:02d}'.format(rtc.datetime()[i])))
            timestamp = '-'.join(datetime)
            if ticks_ms() >= tempoDados:
                dir = windVane1(25)
                pressao = bmp.pressure
                ds18.convert_temp()
                for i in roms:
                    temp = ds18.read_temp(i)
                l = [(f'{timestamp}'),
                    str(vel[0]),
                    str(vel[1]),
                    str(vel[2]),
                    str(dir),
                    (f'{temp:.2f}'),
                    (f'{pressao.strip("hPa")}')]
                datetime.clear()
                pacote = ';'.join(l)
                listaGrava.append(f'{pacote}')
                lora.send_to_wait(f'@{pacote}',SERVER_ADDRESS)
                for i in range(7):
                    l.clear()
                tempoDados = ticks_ms() + 20000
    
except:
    reset()
        

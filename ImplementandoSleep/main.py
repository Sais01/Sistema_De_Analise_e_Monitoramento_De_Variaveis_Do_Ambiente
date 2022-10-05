from umqttsimple import MQTTClient
import ubinascii
import machine
from time import sleep_ms, time, sleep, ticks_ms, ticks_diff, ticks_add
from bmp280 import BME280
import network
import dht
import json


def escreverTextoI2C(conteudo):
  
    texto_escrito = open("i2c.txt", 'a')
    texto_escrito.write (conteudo + "\n")
    texto_escrito.close()

def escreverDados(conteudo):
  
    texto_escrito = open("BMP.txt", 'a')
    texto_escrito.write (conteudo + "\n")
    texto_escrito.close()

#%%%%%%%%%% Realizando comunicação com sensores %%%%%%%%%%%%%
i2c = machine.I2C(scl=machine.Pin(2), sda=machine.Pin(0))

dht11 = dht.DHT11(machine.Pin(1,machine.Pin.IN))#TX
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%% Informações wifi e MQTT %%%%%%%
ssid = 'SAIS'
password = 'cristofer'
mqtt_server = 'demo.thingsboard.io'
user = 'Am9603oArR8V1fRuNyuF'

client_id = ubinascii.hexlify(machine.unique_id())
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%% Tópicos MQTT %%%%%%%%%%%%%
topico_dados = b'bmp/dados'
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%% Configuracao e inicializacao MQTT e Wifi %%%% 
futuro = ticks_ms()

def ativaWifi(rede, senha):
  wifi = network.WLAN(network.STA_IF)
  wifi.active(True)
  if not wifi.isconnected():# Verifica se já estava conectado a uma rede existente
    wifi.connect(rede,senha)
    tentativas = 0
    while not wifi.isconnected() and tentativas < 10:
      sleep_ms(1000)
      tentativas +=1
  escreverDados("Conectou")
  return wifi if wifi.isconnected() else None


def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id=client_id, server=mqtt_server, port=1883, user=user, password="", keepalive=10000)
  client.connect()
  return client

def restart_and_reconnect():
  sleep(10)
  machine.reset()

try:
   rede = ativaWifi(ssid, password)
except:
   escreverDados('Erro no wifi')
   
try:
  client = connect_mqtt()
except OSError as e:
  escreverDados("nao conectou")
  restart_and_reconnect()
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

while True:
    try:
        if ticks_diff(ticks_ms(), futuro) > 0:
            
            pressao = 0
            temperatura_bmp = 0
            temperatura_dht = 0
            umidade = 0
            
            data = dict()
            
            devices = i2c.scan()

            if len(devices) == 0:
                escreverTextoI2C("No i2c device !")
            else:
                escreverTextoI2C("i2c devices found:{}".format(len(devices)))
                bmp = BME280(i2c=i2c)
                
                escreverDados("Temperatura:{}".format(bmp.values[0]))
                temperatura_bmp = bmp.values[0]
                
                escreverDados("Pressao:{}".format(bmp.values[1]))
                pressao = bmp.values[1]

                for device in devices:  
                    escreverTextoI2C("Hexa address: {}".format(hex(device)))  
            
            try:
                dht11.measure()
                
                temperatura_dht = dht11.temperature()
                umidade = dht11.humidity()
            except:
                escreverDados("Deu ruim")
                        
            data["temperatura_dht"] = temperatura_dht
            data["temperatura_bmp"] = temperatura_bmp
            data["pressao"] = pressao
            data["umidade"] = umidade
                        
            data_final=json.dumps(data)
            
            client.publish(topico_dados, data_final)
            
            futuro = ticks_add(ticks_ms(), 5000)
    except OSError as e:
        restart_and_reconnect()

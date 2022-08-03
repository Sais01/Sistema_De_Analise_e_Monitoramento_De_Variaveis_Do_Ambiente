from umqttsimple import MQTTClient
import ubinascii
import machine
import time
from bmp280 import BME280
import network
import dht

def escreverTexto(conteudo):
  
    texto_escrito = open("i2c.txt", 'a')
    texto_escrito.write (conteudo + "\n")
    texto_escrito.close()

def escreverDados(conteudo):
  
    texto_escrito = open("BMP.txt", 'a')
    texto_escrito.write (conteudo + "\n")
    texto_escrito.close()

i2c = machine.I2C(scl=machine.Pin(2), sda=machine.Pin(0))

dht11 = dht.DHT11(machine.Pin(1,machine.Pin.IN))#TX

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

#%%%%% Configuracao e inicializacao MQTT %%%% 
last_message = 0
message_interval = 2

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id=client_id, server=mqtt_server, port=1883, user=user, password="", keepalive=10000)
  client.connect()
  return client

def restart_and_reconnect():
  time.sleep(10)
  machine.reset()

try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
while True:
    try:
        if (time.time() - last_message) > message_interval:
            
            pressao = 0
            temperatura_bmp = 0
            temperatura_dht = 0
            umidade = 0
            
            devices = i2c.scan()

            if len(devices) == 0:
                escreverTexto("No i2c device !")
            else:
                escreverTexto("i2c devices found:{}".format(len(devices)))
                bmp = BME280(i2c=i2c)
                
                escreverDados("Temperatura:{}".format(bmp.values[0]))
                temperatura_bmp = bmp.values[0]
                
                escreverDados("Pressao:{}".format(bmp.values[1]))
                pressao = bmp.values[1]

                for device in devices:  
                    escreverTexto("Hexa address: {}".format(hex(device)))  
            
            dht11.measure()
            
            temperatura_dht = dht11.temperature()
            umidade = dht11.humidity()
            
            dados = "\'temperatura_dht\':\'{}\', \'temperatura_bmp\':\'{}\',\'pressao\':\'{}\', \'umidade\':\'{}\'".format(temperatura_dht,temperatura_bmp, pressao,umidade)

            json_dados = "{"+ dados +"}"
            
            client.publish(topico_dados, json_dados)
            
            last_message = time.time()
    except OSError as e:
        restart_and_reconnect()
    


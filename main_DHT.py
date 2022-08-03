import time
from umqttsimple import MQTTClient
import ubinascii
import micropython
import network
import esp
esp.osdebug(None)
import gc
import dht
from machine import Pin
import machine
from machine import I2C
from bmp280 import BMP280
gc.collect()

dht11 = dht.DHT11(Pin(2,Pin.IN))
bus = machine.I2C(sda=machine.Pin(0),scl=machine.Pin(1))
bmp = BMP280(bus)

#%%%%% Informações wifi e MQTT %%%%%%%
ssid = 'SAIS'
password = 'cristofer'
mqtt_server = 'broker.mqttdashboard.com'

client_id = ubinascii.hexlify(machine.unique_id())
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%% Tópicos MQTT %%%%%%%%%%%%%
topico_temperatura = b'cristofer/temperatura'
topico_umidade = b'cristofer/umidade'
topico_pressao = b'cristofer/pressao'
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%% Configuracao e inicializacao MQTT %%%% 
last_message = 0
message_interval = 5

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')

def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server)
  client.connect()
  print('Connected to {} MQTT broker'.format(mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%% Envio de dados MQTT %%%%%%%%%%%%
while True:
  try:
    if (time.time() - last_message) > message_interval:
      dht11.measure()
      client.publish(topico_temperatura, str(bmp.temperature()))
      client.publish(topico_umidade, str(dht11.humidity()))
      client.publish(topico_pressao, str(bmp.pressure()))
      last_message = time.time()
  except OSError as e:
    restart_and_reconnect()
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
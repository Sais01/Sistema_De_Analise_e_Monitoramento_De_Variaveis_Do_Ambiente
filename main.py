# Scanner i2c en MicroPython | MicroPython i2c scanner
# Renvoi l'adresse en decimal et hexa de chaque device connecte sur le bus i2c
# Return decimal and hexa adress of each i2c device
# https://projetsdiy.fr - https://diyprojects.io (dec. 2017)

import machine
from time import sleep
from bmp280 import *

def escreverTexto(conteudo):
  
    texto_escrito = open("i2c.txt", 'a')
    texto_escrito.write (conteudo + "\n")
    texto_escrito.close()

def escreverDados(conteudo):
  
    texto_escrito = open("BMP.txt", 'a')
    texto_escrito.write (conteudo + "\n")
    texto_escrito.close()

i2c = machine.I2C(scl=machine.Pin(2), sda=machine.Pin(0))
devices = i2c.scan()

if len(devices) == 0:
  escreverTexto("No i2c device !")
else:
  escreverTexto("i2c devices found:{}".format(len(devices)))

  for device in devices:  
    escreverTexto("Hexa address: {}".format(hex(device)))

bmp = BMP280(i2c)
escreverTexto("CHEGOUU")

bmp.use_case(BMP280_CASE_WEATHER)
bmp.oversample(BMP280_OS_HIGH)

bmp.temp_os = BMP280_TEMP_OS_8
bmp.press_os = BMP280_PRES_OS_4

bmp.standby = BMP280_STANDBY_250
bmp.iir = BMP280_IIR_FILTER_2

bmp.spi3w = BMP280_SPI3W_ON

bmp.power_mode = BMP280_POWER_NORMAL

while True:
    escreverDados("TEMP{}, PRESS{}".format(bmp.pressure, bmp.temperature))


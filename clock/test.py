import max7219
from machine import Pin, SPI
from time import sleep

# Настройка SPI
spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)

# 4 матрицы
display = max7219.Matrix8x8(spi, cs, 4)

display.brightness(1)
display.fill(0)
display.show()

# Простой тест: зажечь один пиксель
display.pixel(0,0,1)
display.pixel(7,0,1)
display.pixel(8,0,1)
display.pixel(31,7,1)
display.show()

sleep(2)

# Тест текста
display.fill(0)
display.text('1234',0,0,1)
display.show()
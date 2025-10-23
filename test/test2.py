from machine import Pin
import time

# Определяем пин для светодиода (например, GPIO 2)
led = Pin(2, Pin.OUT)

while True:
    led.value(1)  # Включаем светодиод
    time.sleep(1) # Ждём 1 секунду
    led.value(0)  # Выключаем светодиод
    time.sleep(1) # Ждём 1 секунду
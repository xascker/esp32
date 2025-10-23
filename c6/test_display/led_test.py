from machine import Pin
import neopixel
import time


pin = Pin(8, Pin.OUT)
num_leds = 1
np = neopixel.NeoPixel(pin, num_leds)

# Функция для установки цвета
def set_rgb_color(r, g, b):
    # Устанавливаем цвет для первого светодиода (цвет: (r, g, b))
    np[0] = (r, g, b)
    np.write()

# Пример использования:

# Синий цвет
set_rgb_color(0, 0, 255)  # (0, 0, 255) - синий
time.sleep(2)

# Красный цвет
set_rgb_color(0, 255, 0)  # (255, 0, 0) - красный
time.sleep(2)

# Зеленый цвет
set_rgb_color(255, 0, 0)  # (0, 255, 0) - зеленый
time.sleep(2)

# Белый цвет
set_rgb_color(255, 255, 255)  # (255, 255, 255) - белый
time.sleep(2)

# Выключаем светодиод
set_rgb_color(0, 0, 0)  # Выключаем светодиод
###################################################################

# Функция установки цвета с учётом яркости
def set_rgb_color(r, g, b, brightness=1.0):
    brightness = max(0, min(1, brightness))  # Ограничиваем от 0 до 1
    np[0] = (int(r * brightness), int(g * brightness), int(b * brightness))
    np.write()

# Тест управления яркостью
for b in [1.0, 0.5, 0.2, 0.1, 0]:  # От 100% до 0%
    set_rgb_color(255, 0, 0, b)  
    time.sleep(1)
    
set_rgb_color(0, 0, 0)  # Выключаем светодиод
#######################################################################

def set_rgb_color(r, g, b):
    # Устанавливаем цвет для первого светодиода (цвет: (r, g, b))
    np[0] = (r, g, b)
    np.write()

# Функция для плавного изменения цветов радуги
def rainbow_cycle(delay=50):
    for i in range(256):
        # Плавный переход между красным, зеленым и синим
        set_rgb_color(i, 255 - i, 0)  # Плавно меняем красный и зеленый
        time.sleep_ms(delay)
        
    for i in range(256):
        # Плавный переход между зеленым и синим
        set_rgb_color(255 - i, 0, i)  # Плавно меняем зеленый и синий
        time.sleep_ms(delay)
        
    for i in range(256):
        # Плавный переход между синим и красным
        set_rgb_color(0, i, 255 - i)  # Плавно меняем синий и красный
        time.sleep_ms(delay)

# Запуск эффекта радуги с плавным изменением
while True:
    rainbow_cycle(10)  # Уменьшите значение для более плавных переходов

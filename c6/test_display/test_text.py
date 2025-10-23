from machine import Pin, SPI
import time
import st7789py as st7789

from text_display import *  # Импортируйте ваши функции и классы для отображения текста

# Настройка SPI
spi = SPI(1, baudrate=40000000, sck=Pin(7), mosi=Pin(6))

# Настройка пинов для дисплея
reset = Pin(21, Pin.OUT)
dc = Pin(15, Pin.OUT)
cs = Pin(14, Pin.OUT)
backlight = Pin(22, Pin.OUT)

# Указываем размеры дисплея и настройки (например, xstart и ystart)
tft = st7789.ST7789(spi, 172, 320, reset, dc, cs, backlight=backlight, xstart=34, ystart=0)

# Инициализация дисплея
tft.init()
time.sleep(1)  # Добавляем задержку для стабильной инициализации

# Включаем подсветку
backlight.value(1)
time.sleep(1)

# Создаем экземпляр FontDisplay
font_display = FontDisplay(tft)

# Выводим текст с поворотом
font_display.draw_text("Hello World!", 20, 40, hallfetica_16x16, rotate=True)

# Отправляем буфер на экран
tft.blit_buffer(buffer, 0, 0, 172, 320)

time.sleep(5)  # Задержка для отображения текста 
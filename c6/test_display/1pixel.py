from machine import Pin, SPI
import time
import st7789py as st7789
import framebuf

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

# Создание буфера для рисования с размером дисплея (172x320)
buffer = bytearray(172 * 320 * 2)  # 2 байта на пиксель (RGB565)
fb = framebuf.FrameBuffer(buffer, 172, 320, framebuf.RGB565)

# Красный цвет (RGB565) — используем 0xF800
BLACK = 0x0000
GREEN = 0x001F
BLUE = 0xF800
RED = 0x07E0
YELLOW = 0x07FF
CYAN = 0xF81F
MAGENTA = 0xFFE0
WHITE = 0xFFFF

# Вычисляем центр экрана
center_x = 172 // 2
center_y = 320 // 2

# Нарисовать один пиксель в центре экрана
fb.pixel(center_x, center_y, MAGENTA)

# Отправляем буфер на экран
tft.blit_buffer(buffer, 0, 0, 172, 320)
time.sleep(2)  # Задержка для проверки, чтобы экран успел обновиться
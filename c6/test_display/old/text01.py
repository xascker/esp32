from machine import Pin, SPI
import time
import st7789py as st7789
import framebuf
from fonts.hallfetica16x16 import hallfetica_16x16

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

# Цвет текста (Белый)
WHITE = 0xFFFF
BLACK = 0x0000

# Класс для работы с шрифтом
class FontDisplay:

    # Функция для отрисовки одного символа с поворотом
    def draw_char(self, x, y, char, font_data, char_width, char_height, rotate):
        char_code = ord(char)
        index = (char_code - 32) * (char_width * char_height // 8)  # Сдвиг для символа
        for row in range(char_height):
            for col in range(char_width):
                byte_index = index + (row * char_width + col) // 8
                bit_index = 7 - (col % 8)  # Горизонтальный бит в байте
                if font_data[byte_index] & (1 << bit_index):
                    if rotate:
                        # Поворот текста на 90 градусов (переворачиваем символ)
                        fb.pixel(x + (char_height - row - 1), y + col, WHITE)  # Переворачиваем символ
                    else:
                        fb.pixel(x + col, y + row, WHITE)  # Рисуем пиксель без поворота

    # Функция для вывода текста с возможностью поворота
    def draw_text(self, text, x, y, font, rotate=False):
        if font == hallfetica_16x16:
            char_width  = 16
            char_height = 16
        else:
            print('font not detected')

        spacing = char_height - 5  # Спейсинг между символами для вертикального текста
        for char in text:
            self.draw_char(x, y, char, font, char_width, char_height, rotate)
            if rotate:
                y += spacing  # Сдвигаем по вертикали для следующего символа
            else:
                x += spacing  # Сдвигаем по горизонтали для следующего символа

        # Отправляем буфер на экран
        tft.blit_buffer(buffer, 0, 0, 172, 320)

# Создаем экземпляр FontDisplay и выводим текст с поворотом
font_display = FontDisplay(tft)

# Выводим текст без поворота
#font_display.draw_text("Hello World", 20, 40, hallfetica_16x16, rotate=False)
#time.sleep(2)  # Задержка для отображения текста

# Выводим текст с поворотом
font_display.draw_text("Hello World!", 20, 40, hallfetica_16x16, rotate=True)

time.sleep(5)  # Задержка для отображения текста

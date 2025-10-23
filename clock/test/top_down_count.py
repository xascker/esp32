from machine import Pin, SPI
import machine
import max7219
import framebuf
import time

spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 4)
display.brightness(1)
display.fill(0)

font8x8_digits = {
    '5': [252, 192, 248, 12, 12, 204, 120, 0],
    '4': [28, 60, 108, 204, 254, 12, 30, 0],
    '7': [252, 204, 12, 24, 48, 48, 48, 0],
    '6': [56, 96, 192, 248, 204, 204, 120, 0],
    '1': [48, 112, 48, 48, 48, 48, 252, 0],
    '0': [124, 198, 206, 222, 246, 230, 124, 0],
    '3': [120, 204, 12, 56, 12, 204, 120, 0],
    '2': [120, 204, 12, 56, 96, 204, 252, 0],
    '8': [120, 204, 204, 120, 204, 204, 120, 0],
    '9': [120, 204, 204, 124, 12, 24, 112, 0],
    ':': [0x00, 0xC0, 0xC0, 0x00, 0x00, 0xC0, 0xC0, 0x00],
    ' ': [0, 0, 0, 0, 0, 0, 0, 0]
}

font_widths = {
    '0': 8, '1': 7, '2': 7, '3': 7, '4': 8,
    '5': 7, '6': 7, '7': 7, '8': 7, '9': 7,
    ':': 3, ' ': 1 
}

letter_width = 6

def show_text_mixed(display, text, x=0, y=0):
    for ch in text:
        if ch in font8x8_digits:
            buf = font8x8_digits[ch]
            w = font_widths.get(ch, 8)
            for row in range(8):
                for col in range(w):
                    if buf[row] & (1 << (7-col)):
                        display.pixel(x+col, y+row, 1)
            x += w
        else:
            fb = bytearray(8)
            fbbuf = framebuf.FrameBuffer(fb, 8, 8, framebuf.MONO_HLSB)
            fbbuf.fill(0)
            fbbuf.text(ch, 0, 0, 1)
            for row in range(8):
                for col in range(6):
                    if fbbuf.pixel(col+1, row):
                        display.pixel(x+col, y+row, 1)
            x += letter_width
    display.show()

def scroll_text(display, msg, speed=0.1):
    display_width = display.num * 8
    text_width = 0
    for ch in msg:
        text_width += font_widths.get(ch, 6 if ch.isalpha() else 8)
    for offset in range(text_width + display_width):
        display.fill(0)
        x = display_width - offset
        for ch in msg:
            if ch in font8x8_digits:
                buf = font8x8_digits[ch]
                w = font_widths.get(ch, 8)
                for row in range(8):
                    for col in range(w):
                        if buf[row] & (1 << (7-col)):
                            if 0 <= x+col < display_width:
                                display.pixel(x+col, row, 1)
                x += w
            else:
                fb = bytearray(8)
                fbbuf = framebuf.FrameBuffer(fb, 8, 8, framebuf.MONO_HLSB)
                fbbuf.fill(0)
                fbbuf.text(ch, 0, 0, 1)
                for row in range(8):
                    for col in range(6):
                        if fbbuf.pixel(col+1, row):
                            if 0 <= x+col < display_width:
                                display.pixel(x+col, row, 1)
                x += letter_width
        display.show()
        time.sleep(speed)


#scroll_text(display, "H ello   12:34 W o rld", 0.05)


text = "12:08"
#text = "H ello "
show_text_mixed(display, text)
#scroll_text(display, text, 0.05)

rtc = machine.RTC()
t = rtc.datetime() # (year, month, day, weekday, hour, minute, second, subseconds)
#current_time = "{:02d}:{:02d}".format(t[4], t[5])
#print(current_time)

def textsize(txt):
    size = 0
    for ch in txt:
        if ch in font_widths:
            size += font_widths[ch]
        else:
            size += letter_width
    return size

def get_time():
    return "{:02d}:{:02d}".format(t[4], t[5])

def get_sec(): 
    return t[6]

def get_day():
    MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    month_str = MONTHS[t[1]-1]
    day = t[2]
    weekday_str = WEEKDAYS[(t[3]-1) % 7]

    return f"{month_str} {day:02d} {weekday_str}"


        
        

print("Time:", get_time())
print("Seconds:", get_sec())
print("Day:", get_day())

print("Ширина текста в пикселях:", textsize(text))




def show_digit(display, digit, x, y):
    ch = str(digit)
    if ch in font8x8_digits:
            buf = font8x8_digits[ch]
            w = font_widths.get(ch, 8)
            for row in range(8):
                for col in range(w):
                    if buf[row] & (1 << (7-col)):
                        display.pixel(x+col, y+row, 1)

def animation_to_top(display, number, prev_number=0):
    # Преобразуем числа в строки с ведущими нулями
    number_str = str(number)
    prev_str = str(prev_number)
    max_len = max(len(number_str), len(prev_str))
    while len(number_str) < max_len:
        number_str = '0' + number_str
    while len(prev_str) < max_len:
        prev_str = '0' + prev_str

    digits = list(number_str)
    prev_digits = list(prev_str)

    # Вычисляем X-позиции каждой цифры с учётом ширины
    x_positions = []
    x = 0
    for d in digits:
        x_positions.append(x)
        x += font_widths.get(d, 8)

    # Анимация по 8 пикселей (высота шрифта)
    for i in range(8):
        display.fill(0)
        for idx, d in enumerate(digits):
            prev_d = prev_digits[idx]

            if prev_d != d:
                # Предыдущая цифра уходит вверх
                y_prev = -i
                # Текущая цифра приходит снизу
                y_curr = 8 - i
                show_digit(display, prev_d, x_positions[idx], y_prev)
                show_digit(display, d, x_positions[idx], y_curr)
            else:
                show_digit(display, d, x_positions[idx], 0)
        display.show()
        time.sleep(0.05)
        
def animation_to_down(display, number, prev_number=0):
    # Преобразуем числа в строки с ведущими нулями
    number_str = str(number)
    prev_str = str(prev_number)
    max_len = max(len(number_str), len(prev_str))
    while len(number_str) < max_len:
        number_str = '0' + number_str
    while len(prev_str) < max_len:
        prev_str = '0' + prev_str

    digits = list(number_str)
    prev_digits = list(prev_str)

    # Вычисляем X-позиции с учётом ширины каждой цифры
    x_positions = []
    x = 0
    for d in digits:
        x_positions.append(x)
        x += font_widths.get(d, 8)  # ширина текущей цифры

    # Анимация по 8 пикселей (высота шрифта)
    for i in range(8):
        display.fill(0)
        for idx, d in enumerate(digits):
            prev_d = prev_digits[idx]

            if prev_d != d:
                # Предыдущая цифра уходит вниз
                y_prev = i
                # Текущая цифра приходит сверху
                y_curr = -8 + i
                show_digit(display, prev_d, x_positions[idx], y_prev)
                show_digit(display, d, x_positions[idx], y_curr)
            else:
                show_digit(display, d, x_positions[idx], 0)
        display.show()
        time.sleep(0.1)

prev = 0
for n in range(120):
    animation_to_down(display, n, prev)
    #animation_to_top(display, n, prev)
    prev = n



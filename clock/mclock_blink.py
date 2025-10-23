from machine import Pin, SPI
import machine
import max7219
import framebuf
import time

TIMEZONE_OFFSET = -6

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
    ' ': [0, 0, 0, 0, 0, 0, 0, 0],
    '`': [0, 0, 0, 0, 0, 0, 0, 0] 
}

font_widths = {
    '0': 8, '1': 7, '2': 7, '3': 7, '4': 8,
    '5': 7, '6': 7, '7': 7, '8': 7, '9': 7,
    ':': 3, ' ': 1, '`': 3
}

letter_width = 6
rtc = machine.RTC()

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

def show_digit(display, digit, x, y):
    ch = str(digit)
    if ch in font8x8_digits:
            buf = font8x8_digits[ch]
            w = font_widths.get(ch, 8)
            for row in range(8):
                for col in range(w):
                    if buf[row] & (1 << (7-col)):
                        display.pixel(x+col, y+row, 1)


#text = "11:13"
#text = "H ello "
#show_text_mixed(display, text)
#scroll_text(display, text, 0.05)
#scroll_text(display, "H ello   12:34 W o rld", 0.05)


def textsize(txt):
    size = 0
    for ch in txt:
        if ch in font_widths:
            size += font_widths[ch]
        else:
            size += letter_width
    return size



def get_local_time():
    t = machine.RTC().datetime()  # (year, month, day, weekday, hour, min, sec, ms)
    utc_seconds = time.mktime((t[0], t[1], t[2], t[4], t[5], t[6], 0, 0))
    local_seconds = utc_seconds + TIMEZONE_OFFSET * 3600
    lt = time.localtime(local_seconds)
    return (lt[0], lt[1], lt[2], (lt[6]+1)%7, lt[3], lt[4], lt[5], 0)


def get_day():
    t = machine.RTC().datetime()
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    WEEKDAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    month_str = MONTHS[t[1]-1]
    day = t[2]
    weekday_str = WEEKDAYS[(t[3]-1) % 7]
    return f"{month_str} {day:02d} {weekday_str}"




def clock(display, clock_str, prev_str='', aligning=0):
    ANIMATION_STEPS = 8
    STEP_DELAY = 1 / ANIMATION_STEPS  # суммарно 1 секунда

    digits = list(clock_str)

    # Формируем prev_digits той же длины, что digits
    if prev_str:
        prev_digits = list(prev_str)
        while len(prev_digits) < len(digits):
            prev_digits.append(' ')
    else:
        prev_digits = list(clock_str)

    # Вычисляем X-позиции с учётом ширины каждой цифры
    x_positions = []
    x = aligning  # смещения
    for d in digits:
        x_positions.append(x)
        x += font_widths.get(d, 8)  # ширина текущей цифры

    # Анимация по 8 шагов
    for i in range(ANIMATION_STEPS):
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
        time.sleep(STEP_DELAY)
    
    # ДОБАВЛЕННЫЙ ФИНАЛЬНЫЙ КАДР: фиксируем цифры в конечной позиции. без него оставливается без одного кадра
    display.fill(0)
    for idx, d in enumerate(digits):
        show_digit(display, d, x_positions[idx], 0)
    display.show()
    






# --- заставка перед часами ---
text = "H ello "
scroll_text(display, text, 0.05)
display.show()
time.sleep(0.5)

# --- очищаем экран перед стартом часов ---
display.fill(0)
display.show()



temp = ''
last_sec = -1
while True:
    t = get_local_time()
    current_time = "{:02d}:{:02d}".format(t[4], t[5])
    sec = t[6]  # текущая секунда
    
    # aligning / вырвнивание
    tw = ((32 - textsize(current_time)) + 1) // 2

    # если изменилась минута — плавная анимация смены цифр
    if current_time != temp:
        clock(display, current_time, prev_str=temp, aligning=tw)
        temp = current_time



    # раз в секунду мигаем двоеточием
    if sec != last_sec:
        last_sec = sec

        # если секунда чётная — двоеточие видно, если нечётная — заменяем на пустое
        if sec % 2 == 0:
            clock_str = current_time
        else:
            clock_str = current_time.replace(':', '`')

        display.fill(0)
        show_text_mixed(display, clock_str, tw, 0)
        display.show()



    time.sleep(0.1)



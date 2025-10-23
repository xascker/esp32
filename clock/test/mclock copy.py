from machine import Pin, SPI
import machine
import max7219
import framebuf
import time
from wi_fi import wifi
import uasyncio as asyncio
import settings
import gc

settings.load_settings()

# VCC - >3.3V
# DIN -> 23
# CS -> 5
# SCK -> 18

spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 4)
display.brightness(settings.display_brightness)
display.fill(0)
display.show()

def set_brightness(b):
    b = max(0, min(7, b))
    settings.display_brightness = b
    display.brightness(b)
    settings.save_settings()

def set_timezone(offset):
    settings.TIMEZONE_OFFSET = offset
    settings.save_settings()

def get_brightness():
    return settings.display_brightness

def get_timezone():
    return settings.TIMEZONE_OFFSET


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
        await asyncio.sleep(speed)


def show_digit(display, digit, x, y):
    ch = str(digit)
    if ch in font8x8_digits:
            buf = font8x8_digits[ch]
            w = font_widths.get(ch, 8)
            for row in range(8):
                for col in range(w):
                    if buf[row] & (1 << (7-col)):
                        display.pixel(x+col, y+row, 1)


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
    local_seconds = utc_seconds + settings.TIMEZONE_OFFSET * 3600
    lt = time.localtime(local_seconds)
    return (lt[0], lt[1], lt[2], (lt[6]+1)%7, lt[3], lt[4], lt[5], 0)


def get_day():
    t = get_local_time()
    MONTHS = ["Ja n  ","Fe b  ","M a r  ","A p r  ","M a y  ","Ju n  ","Ju l  ","A u g  "," S e p  ","O ct  ","N o v  ","D e c  "]
    WEEKDAYS = [" M o n "," Tu e "," W e d "," T h u "," Fri "," S a t "," S u n "]
    month_str = MONTHS[t[1]-1]
    day = t[2]
    weekday_str = WEEKDAYS[(t[3]-1) % 7]
    return f"{month_str} {day:02d} {weekday_str}"


def animate_clock(display, new_time, old_time='', aligning=0):
    digits_new = list(new_time)

    # add old time with spaces to match length
    if len(old_time) < len(digits_new):
        old_time = old_time + ' ' * (len(digits_new) - len(old_time))
    digits_old = list(old_time)

    x_positions = []
    x = aligning
    for d in digits_new:
        x_positions.append(x)
        x += font_widths.get(d, 8)

    ANIMATION_STEPS = 8
    for step in range(ANIMATION_STEPS):
        display.fill(0)
        for idx, d_new in enumerate(digits_new):
            d_old = digits_old[idx]
            if d_old != d_new:
                y_old = step
                y_new = -8 + step
                show_digit(display, d_old, x_positions[idx], y_old)
                show_digit(display, d_new, x_positions[idx], y_new)
            else:
                show_digit(display, d_new, x_positions[idx], 0)
        display.show()
        await asyncio.sleep(1 / ANIMATION_STEPS)

    # Final frame
    display.fill(0)
    for idx, d_new in enumerate(digits_new):
        show_digit(display, d_new, x_positions[idx], 0)
    display.show()
    


async def clock_loop():
    temp = ''
    last_scroll_minute = -1
    
    # --- clock hello ---
    ip = wifi.ifconfig()[0]
    text = "H ello " + "    " + ip
    await scroll_text(display, text, 0.05)
    display.fill(0)
    display.show()

    while True:
        t = get_local_time()
        current_time = "{:02d}:{:02d}".format(t[4], t[5])
        sec = t[6]
        minute = t[5]

        tw = ((32 - textsize(current_time)) + 1) // 2

        # blinking :
        clock_str = current_time if sec % 2 == 0 else current_time.replace(':', '`')

        # Show the date every 3 minutes at 17 second
        if (minute % 3 == 0) and (sec == 17) and (last_scroll_minute != minute):
            display.fill(0)
            display.show()
            day_text = get_day()
            await scroll_text(display, day_text + "   ", 0.05)
            display.fill(0)
            display.show()
            last_scroll_minute = minute
            temp = ''
            await asyncio.sleep(0.1)
            continue
        
        # cleanup memory every min
        if sec == 0: 
            import gc
            gc.collect()

        if clock_str != temp:
            await animate_clock(display, clock_str, old_time=temp, aligning=tw)
            temp = clock_str

        await asyncio.sleep(0.1)

from machine import Pin, SPI
import max7219
import framebuf

spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 4)
display.brightness(1)

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
}

def show_text_mixed(display, text, x=0, y=0):
    for ch in text:
        if ch in font8x8_digits:
            buf = font8x8_digits[ch]
            for row in range(8):
                for col in range(8):
                    if buf[row] & (1 << (7-col)):
                        display.pixel(x+col, y+row, 1)
            x += 8
        else:
            display.text(ch, x, y, 1)
            x += 8
    display.show()


display.fill(0)
show_text_mixed(display, "19Ac")


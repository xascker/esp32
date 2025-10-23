"""
    https://javl.github.io/image2cpp/
    Background color: Black
    Invert image colors: true
    Code output format: Plain bytes
"""

import utime
from e_inkv2_library import EPD_4in2
from logo import logo_house

EPD_WIDTH = 400
EPD_HEIGHT = 300

if __name__ == '__main__':
    epd = EPD_4in2()

    epd.image1Gray.fill(0xff)
    epd.EPD_4IN2_V2_Init()
    
    
    logo_width = 128
    logo_height = 128

    # Calculate the starting point to center the logo
    start_x = (EPD_WIDTH - logo_width) // 2
    start_y = (EPD_HEIGHT - logo_height) // 2

    for y in range(logo_height):
        for x in range(logo_width):
            if logo_house[y * (logo_width // 8) + (x // 8)] & (128 >> (x % 8)):
                epd.image1Gray.pixel(start_x + x, start_y + y, epd.black)
    
    
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    epd.delay_ms(5000)
    epd.Sleep()

    

    
    

    




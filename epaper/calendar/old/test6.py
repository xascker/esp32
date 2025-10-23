import utime
from epd4in2v2 import EPD_4in2
#from icons import *
from icon_display import *

EPD_WIDTH = 400
EPD_HEIGHT = 300

if __name__ == '__main__':
    epd = EPD_4in2()

    epd.image1Gray.fill(0xff)
    epd.EPD_4IN2_V2_Init()
    
    icon_display = IconDisplay(epd)
    icon_display.draw_icon(10, 10, sunset_32x32, image4Gray=False)

    
    
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    epd.delay_ms(5000)
    epd.Sleep()



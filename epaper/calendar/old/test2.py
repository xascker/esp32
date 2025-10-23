import utime
from epd4in2v2 import EPD_4in2
#from text_display import FontDisplay
from text_display import *

EPD_WIDTH = 400
EPD_HEIGHT = 300


if __name__ == '__main__':
    epd = EPD_4in2()
    epd.image1Gray.fill(0xff)
    epd.EPD_4IN2_V2_Init()

    text_display = FontDisplay(epd)

    x = 10
    y = 10
    #text = "ABCDabcd"
    text = "Hello World! 1234567"

    
    #text = "Hello World! 123"
    #text_width = len(text) * 20  # 8 пикселей на символ при шрифте 8 пикселей в ширину
    #x = (EPD_WIDTH - text_width) // 2
    #y = (EPD_HEIGHT - 32) // 2  # Размер текста 8 пикселей в высоту


    #text_display.draw_text_ububntu24(x, y, text)
    text_display.draw_text(text, 10, 10, ubuntu_24x32)
    text_display.draw_text(text, 10, 50, ubuntubold_24x32)
    
    text_display.draw_text(text, 10, 100, arial_16x16)
    text_display.draw_text(text, 10, 130, arialbold_16x16)
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    epd.delay_ms(1000) 
    
    text_display.draw_text(text, 10, 160, hallfetica_16x16)
    epd.image1Gray.text(text, 10, 190, epd.black)
    

    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    epd.delay_ms(5000) 
    epd.Sleep()  
    

    

    
    

    




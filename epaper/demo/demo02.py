import utime
from e_inkv2_library import EPD_4in2

EPD_WIDTH = 400
EPD_HEIGHT = 300

if __name__ == '__main__':
    epd = EPD_4in2()

    epd.image1Gray.fill(0xff)
    epd.image4Gray.fill(0xff)

    epd.EPD_4IN2_V2_Init()
    #epd.EPD_4IN2_V2_Init_4Gray()
    #epd.EPD_4IN2_V2_Init_Fast(epd.Seconds_1_5S)

    
    # Вычисление координат для центра текста
    text = "Hello World!"
    text_width = len(text) * 8  # 8 пикселей на символ при шрифте 8 пикселей в ширину
    start_x = (EPD_WIDTH - text_width) // 2
    start_y = (EPD_HEIGHT - 8) // 2  # Размер текста 8 пикселей в высоту

    epd.image1Gray.text(text, start_x, start_y, epd.black)
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    #epd.EPD_4IN2_V2_Display_Fast(epd.buffer_1Gray)
    epd.delay_ms(1000)
     

    #epd.image4Gray.text(text, start_x, start_y, epd.grayish)
    #epd.EPD_4IN2_V2_4GrayDisplay(epd.buffer_4Gray)
    
    epd.image1Gray.vline(10, 90, 60, epd.black)
    epd.image1Gray.vline(90, 90, 60, epd.black)
    epd.image1Gray.hline(10, 90, 80, epd.black)
    epd.image1Gray.hline(10, 150, 80, epd.black)
    epd.image1Gray.line(10, 90, 90, 150, epd.black)
    epd.image1Gray.line(90, 90, 10, 150, epd.black)
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)


    epd.delay_ms(5000)
    epd.Sleep()

    

    
    

    




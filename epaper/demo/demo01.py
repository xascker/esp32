import utime
from e_inkv2_library import EPD_4in2

EPD_WIDTH = 400
EPD_HEIGHT = 300


if __name__=='__main__':
    
    epd = EPD_4in2()
    
    epd.image1Gray.fill(0xff)
    epd.image4Gray.fill(0xff)

    print("Full brush")
    epd.EPD_4IN2_V2_Init()
    epd.image1Gray.text("Waveshare", 5, 10, epd.black)
    epd.image1Gray.text("Pico_ePaper-4.2", 5, 40, epd.black)
    epd.image1Gray.text("Raspberry Pico", 5, 70, epd.black)
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    epd.delay_ms(2000)
    
    epd.image1Gray.vline(10, 90, 60, epd.black)
    epd.image1Gray.vline(90, 90, 60, epd.black)
    epd.image1Gray.hline(10, 90, 80, epd.black)
    epd.image1Gray.hline(10, 150, 80, epd.black)
    epd.image1Gray.line(10, 90, 90, 150, epd.black)
    epd.image1Gray.line(90, 90, 10, 150, epd.black)
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    epd.delay_ms(2000)
    
    print("Quick refresh")
    epd.EPD_4IN2_V2_Init_Fast(epd.Seconds_1_5S)
    epd.image1Gray.rect(10, 180, 50, 80, epd.black)
    epd.image1Gray.fill_rect(70, 180, 50, 80, epd.black)
    epd.EPD_4IN2_V2_Display_Fast(epd.buffer_1Gray)
    epd.delay_ms(2000)

    print("partial refresh")
    for i in range(0, 10):
        print(str(i))
        epd.image1Gray.fill_rect(60, 270, 10, 10, epd.white)
        epd.image1Gray.text(str(i), 62, 272, epd.black)
        epd.EPD_4IN2_V2_PartialDisplay(epd.buffer_1Gray)
        epd.delay_ms(500)
    
    print("Four grayscale refresh")
    epd.EPD_4IN2_V2_Init_4Gray()
    epd.image4Gray.fill_rect(150, 10, 250, 30, epd.black)
    epd.image4Gray.text('GRAY1 with black background',155, 21, epd.white)
    epd.image4Gray.text('GRAY2 with white background',155, 51, epd.grayish)
    epd.image4Gray.text('GRAY3 with white background',155, 81, epd.darkgray)
    epd.image4Gray.text('GRAY4 with white background',155, 111, epd.black)
    epd.EPD_4IN2_V2_4GrayDisplay(epd.buffer_4Gray)
    epd.delay_ms(5000)

    print("Clear")
    epd.EPD_4IN2_V2_Init()
    epd.EPD_4IN2_V2_Clear()
    
    print("Enter sleep mode ")
    epd.Sleep()

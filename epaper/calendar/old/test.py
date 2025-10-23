import utime
from epd4in2v2 import EPD_4in2


if __name__ == '__main__':
    epd = EPD_4in2()
    epd.image1Gray.fill(0xff)
    epd.EPD_4IN2_V2_Init()
    epd.image4Gray.fill(0xff)
    epd.EPD_4IN2_V2_Init_4Gray()

    
    x = 10
    y = 10
    text = "AB"
    epd.image1Gray.text(text, x, y, epd.black)
    
    
    
    
    
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    epd.delay_ms(5000) 
    epd.Sleep()  
    

    


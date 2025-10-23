import utime
from epd4in2v2 import EPD_4in2
from influxdb_data import *
from graphs import *
from calendar import CalendarDisplay
from battery import DrawBattery

EPD_WIDTH = 400
EPD_HEIGHT = 300


if __name__ == '__main__':
    epd = EPD_4in2()
    epd.image1Gray.fill(0xff)
    epd.image4Gray.fill(0xff)
    epd.EPD_4IN2_V2_Init()
    #epd.EPD_4IN2_V2_Init_4Gray()
    
    battery = DrawBattery(epd)
    battery.draw_battery(image4Gray=False)
    
    
    
    
    #epd.EPD_4IN2_V2_4GrayDisplay(epd.buffer_4Gray)
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    epd.delay_ms(5000) 
    epd.Sleep()
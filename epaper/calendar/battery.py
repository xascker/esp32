import utime
from machine import Pin, ADC


adc = ADC(Pin(34))  # 34 PIN
# ADC Setting 
adc.width(ADC.WIDTH_12BIT)  # 12 bits, value range 0-4095
adc.atten(ADC.ATTN_0DB) 

raw_value = adc.read()
voltage = raw_value * (1.698 / 4095)

input_voltage = voltage * ((20 + 10) / 10)  # R1 = 20kΩ and R2 = 10kΩ


class DrawBattery:
    def __init__(self, epd):
        self.epd = epd
    
    def draw_battery(self, image4Gray):

        battery_width = 40
        battery_height = 15
        battery_x = 355
        battery_y = 0
        
        # draw the battery itself (the main part)
        if image4Gray:
            self.epd.image4Gray.fill_rect(battery_x, battery_y, battery_width, battery_height, self.epd.white)
            self.epd.image4Gray.rect(battery_x, battery_y, battery_width, battery_height, self.epd.black)
        else:
            self.epd.image1Gray.fill_rect(battery_x, battery_y, battery_width, battery_height, self.epd.white)
            self.epd.image1Gray.rect(battery_x, battery_y, battery_width, battery_height, self.epd.black)
        
        # Draw the battery terminal on the right
        terminal_width = 4
        terminal_height = 8
        if image4Gray:
            self.epd.image4Gray.fill_rect(battery_x + battery_width, battery_y + (battery_height // 2) - (terminal_height // 2), terminal_width, terminal_height, self.epd.black)
        else:
            self.epd.image1Gray.fill_rect(battery_x + battery_width, battery_y + (battery_height // 2) - (terminal_height // 2), terminal_width, terminal_height, self.epd.black)


        if image4Gray:
            self.epd.image4Gray.text("{:.2f}".format(input_voltage), battery_x + 3, battery_y + 5, self.epd.black)
            self.epd.image4Gray.text("{:.0f}%".format(self.calculate_battery_percent(input_voltage)), battery_x - 40, battery_y + 5, self.epd.black)
        else:
            self.epd.image1Gray.text("{:.2f}".format(input_voltage), battery_x + 3, battery_y + 5, self.epd.black)
            self.epd.image1Gray.text("{:.0f}%".format(self.calculate_battery_percent(input_voltage)), battery_x - 40, battery_y + 5, self.epd.black)
            
    
    def calculate_battery_percent(self, voltage):
        max_voltage = 4.1  
        min_voltage = 3.3  

        if voltage >= max_voltage:
            return 100  
        elif voltage <= min_voltage:
            return 0  
        else:
            return int((voltage - min_voltage) / (max_voltage - min_voltage) * 100)
    
        

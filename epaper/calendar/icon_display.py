from icons import *

icon_width = 32
icon_height = 32

class IconDisplay:
    def __init__(self, epd):
        self.epd = epd
                    
    def draw_icon(self, start_x, start_y, icon_name, image4Gray):
        for y in range(icon_height):
            for x in range(icon_width):
                if icon_name[y * (icon_width // 8) + (x // 8)] & (128 >> (x % 8)):
                    if image4Gray:
                        self.epd.image4Gray.pixel(start_x + x, start_y + y, self.epd.darkgray)
                    else:
                        self.epd.image1Gray.pixel(start_x + x, start_y + y, self.epd.black)
                        
                    
    


           
            
            
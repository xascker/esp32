#from fonts.ubuntu24x32 import ubuntu_24x32
#from fonts.ubuntubold24x32 import ubuntubold_24x32
#from fonts.arial16x16 import arial_16x16
#from fonts.arialbold16x16 import arialbold_16x16
from fonts.hallfetica16x16 import hallfetica_16x16

class FontDisplay:
    def __init__(self, epd):
        self.epd = epd
                    
    def draw_char(self, x, y, char, font_data, char_width, char_height, image4Gray):
        char_code = ord(char)
        index = (char_code - 32) * (char_width * char_height // 8)  # Offset for symbol
        for row in range(char_height):
            for col in range(char_width):
                byte_index = index + (row * char_width + col) // 8
                bit_index = 7 - (col % 8)  # Horizontal bit within a byte
                if font_data[byte_index] & (1 << bit_index):
                    if image4Gray:
                        self.epd.image4Gray.pixel(x + col, y + row, self.epd.black)
                    else:
                        self.epd.image1Gray.pixel(x + col, y + row, self.epd.black)
                    
    def draw_text4Gray(self, text, x, y, font):
        char_width  = 16
        char_height = 16
        spacing = char_width - 5  # Spacing between characters
        for char in text:
            self.draw_char(x, y, char, font, char_width, char_height, image4Gray=True)
            x += spacing  # Move to the next symbol
                    
    
    #def draw_text(self, text, x, y, font):
    #    if font == ubuntu_24x32 or font == ubuntubold_24x32:
    #        char_width  = 24
    #        char_height = 32
    #    elif font == arial_16x16 or font == arialbold_16x16 or font == hallfetica_16x16:
    #        char_width  = 16
    #        char_height = 16
    #    else:
    #        print('font not detected')

    #    spacing = char_width - 5  # Spacing between characters
    #    for char in text:
    #        self.draw_char(x, y, char, font, char_width, char_height, image4Gray=False)
    #        x += spacing  # Move to the next symbol

           
            
            
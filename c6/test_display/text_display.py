#from fonts.ubuntu24x32 import ubuntu_24x32
#from fonts.ubuntubold24x32 import ubuntubold_24x32
#from fonts.arial16x16 import arial_16x16
#from fonts.arialbold16x16 import arialbold_16x16
from fonts.hallfetica16x16 import hallfetica_16x16
import framebuf


buffer = bytearray(172 * 320 * 2)  # 2 bytes per pixel 
fb = framebuf.FrameBuffer(buffer, 172, 320, framebuf.RGB565)

WHITE = 0xFFFF
BLACK = 0x0000

class FontDisplay:
    
    def draw_char(self, x, y, char, font_data, char_width, char_height, rotate):
        char_code = ord(char)
        index = (char_code - 32) * (char_width * char_height // 8)  
        for row in range(char_height):
            for col in range(char_width):
                byte_index = index + (row * char_width + col) // 8
                bit_index = 7 - (col % 8)  
                if font_data[byte_index] & (1 << bit_index):
                    if rotate:
                        fb.pixel(x + (char_height - row - 1), y + col, WHITE) 
                    else:
                        fb.pixel(x + col, y + row, WHITE)  

    def draw_text(self, text, x, y, font, rotate=False):
        if font == hallfetica_16x16:
            char_width  = 16
            char_height = 16
        else:
            print('font not detected')

        spacing = char_height - 5  
        for char in text:
            self.draw_char(x, y, char, font, char_width, char_height, rotate)
            if rotate:
                y += spacing  
            else:
                x += spacing 



           
            
            

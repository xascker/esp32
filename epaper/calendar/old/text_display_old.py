from font32x32 import font_32x32

class FontDisplay:
    def __init__(self, epd):
        self.epd = epd

    def draw_text(self, x, y, text):
        spacing = 30  # Space between characters
        for char in text:
            if char in font32x32:
                self.draw_char(x, y, char)
                x += spacing  # Move x position by character width + spacing
            else:
                x += spacing  # Skip unknown characters

    def draw_char(self, x, y, char):
        font = font32x32.get(char)
        if font:
            for row, line in enumerate(font):
                for col in range(8):
                    if (line >> (7 - col)) & 1:
                        self.epd.image1Gray.pixel(x + col, y + row, self.epd.black)
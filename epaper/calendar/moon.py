import utime
#from moon_icons import *

icon_width = 64
icon_height = 64

class MoonPhase:
    def __init__(self, epd):
        self.epd = epd
        # Используем известную дату новолуний: 1 ноября 2024 года 
        self.known_new_moon = 1730419200  # 1 ноября 2024 года 
        # Период цикла Луны в днях
        self.moon_cycle = 29.5305882
        
    def draw_moon_phase(self, moon_x, moon_y, image4Gray):
        current_time = utime.time()
        
        # Количество дней с момента известного новолуний
        days_since_new_moon = (current_time - self.known_new_moon) / (24 * 3600)

        # Вычисляем остаток от деления на цикл Луны
        phase = days_since_new_moon % self.moon_cycle
        #print(phase)

        if phase < 0.5 or phase >= 28:
            self.draw_icon(moon_x, moon_y, self.load_icon("moon_black_64x64"), image4Gray)
            #return "Новолуние"
        elif phase < 6.5:
            self.draw_icon(moon_x, moon_y, self.load_icon("moon_phase_01_64x64"), image4Gray)
            #return "Растущий серп"
        elif phase < 8.5:
            self.draw_icon(moon_x, moon_y, self.load_icon("first_half_moon_64x64"), image4Gray)
            #return "Первая четверть"
        elif phase < 14:
            self.draw_icon(moon_x, moon_y, self.load_icon("moon_phase_03_64x64"), image4Gray)
            #return "Растущая Луна"
        elif phase < 16:
            self.draw_icon(moon_x, moon_y, self.load_icon("moon_full_64x64"), image4Gray)
            #return "Полнолуние"
        elif phase < 20:
            self.draw_icon(moon_x, moon_y, self.load_icon("moon_phase_05_64x64"), image4Gray)
            #return "Убывающая Луна"
        elif phase < 22:
            self.draw_icon(moon_x, moon_y, self.load_icon("last_half_moon_64x64"), image4Gray)
            #return "Последняя четверть"
        elif phase < 28:
            self.draw_icon(moon_x, moon_y, self.load_icon("moon_phase_07_64x64"), image4Gray)
            #return "Убывающий серп"
        else:
            return "Неизвестно"
        
        
    def load_icon(self, icon_name):
        try:
            with open(f"moons/{icon_name}.bin", "rb") as f:
                icon_data = f.read()
            return icon_data
        except Exception as e:
            print(f"Ошибка загрузки иконки {icon_name}: {e}")
            return None

    def draw_icon(self, start_x, start_y, icon_data, image4Gray, icon_width=64, icon_height=64):
        for y in range(icon_height):
            for x in range(icon_width):
                byte_index = y * (icon_width // 8) + (x // 8)
                bit_index = 7 - (x % 8)
                bit = (icon_data[byte_index] >> bit_index) & 1

                if bit:
                    if image4Gray:
                        self.epd.image4Gray.pixel(start_x + x, start_y + y, self.epd.darkgray)
                    else:
                        self.epd.image1Gray.pixel(start_x + x, start_y + y, self.epd.black)




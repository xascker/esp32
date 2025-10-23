import utime
import time
import ntptime
from dates import x_dates
from set_utc import GetUtc

start_x = 1
start_y = 1
description_x = 245
description_y = 30
CELL_WIDTH = 33   # Ширина ячейки для каждого дня
CELL_HEIGHT = 20  # Высота ячейки для каждого дня
HEADER_HEIGHT = 22  # Высота название месяца
TEXT_CENTERING = 7 

# Получение текущей даты
ntptime.settime()
current_time = time.localtime()
utc_fetcher = GetUtc()
local_utc_hours = utc_fetcher.get_local_utc()
local_utc_seconds = local_utc_hours * 3600
local_timestamp = int(time.mktime(current_time) + local_utc_seconds)
local_time = time.localtime(local_timestamp)
year = local_time[0]
month = local_time[1]
day = local_time[2]
weekday = local_time[6] # День недели (0 - понедельник, 6 - воскресенье)

days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Количество дней в текущем месяце
# Определяем количество дней в месяце
days_in_month = [31, 28 + (1 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 0), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
days_in_current_month = days_in_month[month - 1]

# Получаем день недели для первого числа месяца
first_day_of_month = time.mktime((year, month, 1, 0, 0, 0, 0, 0, -1))
first_weekday = time.localtime(first_day_of_month)[6]

class CalendarDisplay:
    def __init__(self, epd):
        self.epd = epd
    
    def draw_calendar(self, start_x, start_y):
        # Название месяца
        self.epd.image4Gray.text(months[month - 1], start_x + (CELL_WIDTH * 3) - 30, start_y + 10, self.epd.black)  # Центрирование

        # Рисуем шапку для дней недели
        for i in range(7):
            if i < 5:  # Пн-Пт - черная
                self.epd.image4Gray.fill_rect(start_x + i * CELL_WIDTH, start_y + HEADER_HEIGHT, CELL_WIDTH, 20, self.epd.black)
                self.epd.image4Gray.text(days_of_week[i], start_x + i * CELL_WIDTH + TEXT_CENTERING, start_y + HEADER_HEIGHT + TEXT_CENTERING, self.epd.white)
            else:  # Сб, Вс - темно-серая
                self.epd.image4Gray.fill_rect(start_x + i * CELL_WIDTH, start_y + HEADER_HEIGHT, CELL_WIDTH, 20, self.epd.darkgray)
                self.epd.image4Gray.text(days_of_week[i], start_x + i * CELL_WIDTH + TEXT_CENTERING, start_y + HEADER_HEIGHT + TEXT_CENTERING, self.epd.black)

        # Рисуем числа в календаре
        x_offset = 0
        y_offset = start_y + HEADER_HEIGHT + CELL_HEIGHT  # Начинаем сразу после шапки
        current_row = 0  # Начинаем с первой строки
        description_to_display = None 

        for i in range(1, days_in_current_month + 1):
            day_of_week = (first_weekday + i - 1) % 7  # Определяем день недели для текущего дня
            x = start_x + (day_of_week) * CELL_WIDTH  # Расположение по горизонтали
            y = y_offset + current_row * CELL_HEIGHT  # Расположение по вертикали

            # Заливаем фон для "Sat" (суббота, индекс 5) и "Sun" (воскресенье, индекс 6) светло-серым
            if day_of_week == 5 or day_of_week == 6:  # Суббота и Вc
                self.epd.image4Gray.fill_rect(x, y, CELL_WIDTH, CELL_HEIGHT, self.epd.grayish)  # Заливка светло-серым для субботы и вс
                
            # Проверяем, нужно ли выделить дату
            x_day = any(m == months[month - 1] and d == i for m, d in x_dates.keys())
            if x_day:
                self.epd.image4Gray.fill_rect(x, y, CELL_WIDTH, CELL_HEIGHT, self.epd.darkgray)

            # Если это текущий день, рисуем черный текст на темносером фоне
            if i == day:
                #self.epd.image4Gray.fill_rect(x, y, CELL_WIDTH, CELL_HEIGHT, self.epd.darkgray)  # темно-серый фон для текущего дня
                # рисуем рамку вокруг ячейки
                self.epd.image4Gray.vline(x, y, CELL_HEIGHT, self.epd.black)  # Левая граница
                self.epd.image4Gray.vline(x + CELL_WIDTH - 1, y, CELL_HEIGHT, self.epd.black)  # Правая граница
                self.epd.image4Gray.hline(x, y, CELL_WIDTH, self.epd.black)  # Верхняя граница
                self.epd.image4Gray.hline(x, y + CELL_HEIGHT - 1, CELL_WIDTH, self.epd.black)  # Нижняя граница
                self.epd.image4Gray.text(str(i), x + TEXT_CENTERING, y + TEXT_CENTERING, self.epd.black)  # черный текст для текущего дня
                
                description_to_display = x_dates.get((months[month - 1], i), None)
            else:
                # Рисуем все числа черным
                self.epd.image4Gray.text(str(i), x + TEXT_CENTERING, y + TEXT_CENTERING, self.epd.black)

            # Если дошли до конца недели (суббота или воскресенье), переходим на следующую строку
            if day_of_week == 6:  # Воскресенье (последний день недели)
                current_row += 1

            #Отображение описания дня, если оно есть
            if description_to_display:
                self.epd.image4Gray.text(description_to_display, description_x, description_y , self.epd.black)
                #text_display = FontDisplay(self.epd)
                #text_display.draw_text4Gray(description_to_display, description_x, description_y, hallfetica_16x16)
         
         


import utime
import time
from epd4in2v2 import EPD_4in2

EPD_WIDTH = 400
EPD_HEIGHT = 300


start_x = 1
start_y = 1
CELL_WIDTH = 33   # Ширина ячейки для каждого дня
CELL_HEIGHT = 20  # Высота ячейки для каждого дня
HEADER_HEIGHT = 22  # Высота название месяца
TEXT_CENTERING = 7 

# Получение текущей даты
current_time = time.localtime()
year = current_time[0]
month = current_time[1]
day = current_time[2]
weekday = current_time[6]  # День недели (0 - понедельник, 6 - воскресенье)


days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Количество дней в текущем месяце
# Определяем количество дней в месяце
days_in_month = [31, 28 + (1 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 0), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
days_in_current_month = days_in_month[month - 1]

# Получаем день недели для первого числа месяца
first_day_of_month = time.mktime((year, month, 1, 0, 0, 0, 0, 0, -1))
first_weekday = time.localtime(first_day_of_month)[6]

if __name__ == '__main__':
    epd = EPD_4in2()
    epd.EPD_4IN2_V2_Init_4Gray()
    epd.image4Gray.fill(0xff)

    # Название месяца
    epd.image4Gray.text(months[month - 1], start_x + (CELL_WIDTH * 3) - 30, start_y + 10, epd.black)  # Центрирование

    # Рисуем шапку для дней недели
    for i in range(7):
        if i < 5:  # Пн-Пт - черная
            epd.image4Gray.fill_rect(start_x + i * CELL_WIDTH, start_y + HEADER_HEIGHT, CELL_WIDTH, 20, epd.black)
            epd.image4Gray.text(days_of_week[i], start_x + i * CELL_WIDTH + TEXT_CENTERING, start_y + HEADER_HEIGHT + TEXT_CENTERING, epd.white)
        else:  # Сб, Вс - темно-серая
            epd.image4Gray.fill_rect(start_x + i * CELL_WIDTH, start_y + HEADER_HEIGHT, CELL_WIDTH, 20, epd.darkgray)
            epd.image4Gray.text(days_of_week[i], start_x + i * CELL_WIDTH + TEXT_CENTERING, start_y + HEADER_HEIGHT + TEXT_CENTERING, epd.black)

    # Рисуем числа в календаре
    x_offset = 0
    y_offset = start_y + HEADER_HEIGHT + CELL_HEIGHT  # Начинаем сразу после шапки
    current_row = 0  # Начинаем с первой строки

    for i in range(1, days_in_current_month + 1):
        day_of_week = (first_weekday + i - 1) % 7  # Определяем день недели для текущего дня
        x = start_x + (day_of_week) * CELL_WIDTH  # Расположение по горизонтали
        y = y_offset + current_row * CELL_HEIGHT  # Расположение по вертикали

        # Заливаем фон для "Sat" (суббота, индекс 5) и "Sun" (воскресенье, индекс 6) светло-серым
        if day_of_week == 5 or day_of_week == 6:  # Суббота и Вc
            epd.image4Gray.fill_rect(x, y, CELL_WIDTH, CELL_HEIGHT, epd.grayish)  # Заливка светло-серым для субботы и вс

        # Если это текущий день, рисуем черный текст на темносером фоне
        if i == day:
            epd.image4Gray.fill_rect(x, y, CELL_WIDTH, CELL_HEIGHT, epd.darkgray)  # темно-серый фон для текущего дня
            epd.image4Gray.text(str(i), x + TEXT_CENTERING, y + TEXT_CENTERING, epd.black)  # черный текст для текущего дня
        else:
            # Рисуем все числа черным
            epd.image4Gray.text(str(i), x + TEXT_CENTERING, y + TEXT_CENTERING, epd.black)

        # Если дошли до конца недели (суббота или воскресенье), переходим на следующую строку
        if day_of_week == 6:  # Воскресенье (последний день недели)
            current_row += 1

 
    epd.EPD_4IN2_V2_4GrayDisplay(epd.buffer_4Gray)
    epd.delay_ms(5000)
    epd.Sleep()
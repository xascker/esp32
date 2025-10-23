import network
import urequests
import ujson
import time
from epd4in2v2 import EPD_4in2

EPD_WIDTH = 400
EPD_HEIGHT = 300

influxdb = 'http://192.168.1.250:8086'
local_utc = -7
graph_range = '6h'

# Функция для кодирования строки запроса
def url_encode(string):
    return string.replace(' ', '%20').replace('"', '%22').replace("'", '%27')

# Функция для форматирования времени с учётом часового пояса
def format_time(utc_time, timezone_offset):
    try:
        # Убираем "Z" и разбиваем строку
        time_part = utc_time.split('T')[1].split('.')[0]
        hours, minutes, seconds = map(int, time_part.split(':'))

        # Переводим в секунды и добавляем смещение
        total_seconds = hours * 3600 + minutes * 60 + seconds + timezone_offset

        # Пересчитываем часы, минуты, секунды
        total_seconds %= 24 * 3600
        local_hours = total_seconds // 3600
        local_minutes = (total_seconds % 3600) // 60

        return f"{local_hours:02}:{local_minutes:02}"
    except Exception as e:
        return "--:--"

# Функция для отрисовки графика
def draw_graph(data, timestamps, epd, timezone_offset, start_x, start_y, graph_width, graph_height, show_all_labels):
    epd.image1Gray.fill(0xff)  # Очистка экрана

    # Определяем диапазоны
    max_temp = max(data)
    min_temp = min(data)
    temp_range = max_temp - min_temp if max_temp != min_temp else 1

    # Нормализация по времени
    time_range = len(timestamps) - 1

    # Рисуем оси
    margin = 5  # Отступ для меток внутри графика
    epd.image1Gray.vline(start_x, start_y, graph_height, epd.black)  # Ось Y
    epd.image1Gray.hline(start_x, start_y + graph_height, graph_width, epd.black)  # Ось X

    # Рисуем метки для оси Y (начало, середина и конец)
    for i, position in enumerate([0, 0.5, 1]):
        y = start_y + graph_height - int(position * graph_height)
        temp_label = round(min_temp + position * temp_range, 1)
        epd.image1Gray.text(str(temp_label), start_x + 3, y - 10, epd.black)  # Отступ для текста

    # Рисуем метки для оси X
    step_x = graph_width // time_range
    if show_all_labels:
        for i in range(len(timestamps)):
            x = start_x + i * step_x
            time_label = format_time(timestamps[i], timezone_offset)
            epd.image1Gray.text(time_label, x - 10, start_y + graph_height + 5, epd.black)  # Снизу графика
    else:
        for i, position in enumerate([0, 0.5, 1]):
            index = int(position * time_range)
            x = start_x + index * step_x
            time_label = format_time(timestamps[index], timezone_offset)
            epd.image1Gray.text(time_label, x - 10, start_y + graph_height + 5, epd.black)  # Снизу графика

    # Рисуем график
    for i in range(1, len(data)):
        x1 = start_x + (i - 1) * step_x
        y1 = start_y + graph_height - int((data[i - 1] - min_temp) / temp_range * graph_height)
        x2 = start_x + i * step_x
        y2 = start_y + graph_height - int((data[i] - min_temp) / temp_range * graph_height)
        epd.image1Gray.line(x1, y1, x2, y2, epd.black)

    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)

# Основная программа
wifi = network.WLAN(network.STA_IF)

if wifi.isconnected():
    url = influxdb+ "/query"
    query = "SELECT * FROM temp WHERE time > now() - " + graph_range + " AND \"sensor\" = 'bme' AND \"location\" = 'inside'"
    full_url = url + "?db=meteo&q=" + url_encode(query)

    response = urequests.get(full_url)

    if response.status_code == 200:
        try:
            data = ujson.loads(response.text)
            values = data['results'][0]['series'][0]['values']

            # Извлекаем время и температуру
            timestamps = [item[0] for item in values]
            temperatures = [item[3] for item in values]

            # Инициализация дисплея
            epd = EPD_4in2()
            epd.EPD_4IN2_V2_Init()

            # Размеры и положение графика
            start_x = 200
            start_y = 100
            graph_width = 150
            graph_height = 80

            # Часовой пояс UTC -7 (MST)
            timezone_offset = local_utc * 3600

            # Флаг отображения всех меток
            show_all_labels = True  # Измените на True для отображения всех меток

            # Рисуем график
            draw_graph(temperatures, timestamps, epd, timezone_offset, start_x, start_y, graph_width, graph_height, show_all_labels)

            epd.delay_ms(5000)
            epd.Sleep()

        except Exception as e:
            print("Data processing error:", e)
    else:
        print("Request error:", response.status_code)
    response.close()
else:
    print("The device is not connected to Wi-Fi network")
import network
import urequests
import ujson
from set_utc import GetUtc


utc_fetcher = GetUtc()
local_utc = utc_fetcher.get_local_utc()

#local_utc = -7 
timezone_offset = local_utc * 3600


class GraphDrawer:
    def __init__(self, epd):
        self.epd = epd
        

    def draw_graph(self, data, timestamps, start_x, start_y, graph_width, graph_height, show_all_labels, image4Gray):
        max_temp = max(data)
        min_temp = min(data)
        last_value = data[-1]
        temp_range = max_temp - min_temp if max_temp != min_temp else 1

        time_range = len(timestamps) - 1

        # Рисуем метки для оси X
        step_x = graph_width // time_range
        if show_all_labels:
            for i in range(len(timestamps)):
                x = start_x + i * step_x
                time_label = self.format_time(timestamps[i], timezone_offset)
                if image4Gray:
                    self.epd.image4Gray.text(time_label, x - 10, start_y + graph_height + 5, self.epd.black)  # Снизу графика
                else:
                    self.epd.image1Gray.text(time_label, x - 10, start_y + graph_height + 5, self.epd.black)  # Снизу графика
        else:
            for i, position in enumerate([0, 0.5, 1]):
                index = int(position * time_range)
                x = start_x + index * step_x
                time_label = self.format_time(timestamps[index], timezone_offset)
                if image4Gray:
                    self.epd.image4Gray.text(time_label, x - 10, start_y + graph_height + 5, self.epd.black)  # Снизу графика
                else:
                    self.epd.image1Gray.text(time_label, x - 10, start_y + graph_height + 5, self.epd.black)  # Снизу графика

        # Рисуем график
        for i in range(1, len(data)):
            x1 = start_x + (i - 1) * step_x
            y1 = start_y + graph_height - int((data[i - 1] - min_temp) / temp_range * graph_height)
            x2 = start_x + i * step_x
            y2 = start_y + graph_height - int((data[i] - min_temp) / temp_range * graph_height)
            if image4Gray:
                #self.epd.image4Gray.fill_rect(x1, min(y1, y2), x2 - x1, start_y + graph_height - min(y1, y2), self.epd.grayish)
                for x in range(x1, x2 + 1):
                    y = int(y1 + (y2 - y1) * (x - x1) / (x2 - x1))
                    self.epd.image4Gray.line(x, y, x, start_y + graph_height, self.epd.grayish)
                self.epd.image4Gray.line(x1, y1, x2, y2, self.epd.darkgray)
            else:
                self.epd.image1Gray.line(x1, y1, x2, y2, self.epd.black)
        
        # Рисуем оси
        margin = 5  # Отступ для меток внутри графика
        if image4Gray:
            self.epd.image4Gray.vline(start_x, start_y, graph_height, self.epd.black)  # Ось Y
            self.epd.image4Gray.hline(start_x, start_y + graph_height, graph_width, self.epd.black)  # Ось X
        else:
            self.epd.image1Gray.vline(start_x, start_y, graph_height, self.epd.black)  # Ось Y
            self.epd.image1Gray.hline(start_x, start_y + graph_height, graph_width, self.epd.black)  # Ось X
                
        # Рисуем метки для оси Y, если show_all_labels включено
        if show_all_labels:
            # Шаг между метками по оси Y
            num_labels = 10  # Количество меток на оси Y
            step_y = graph_height / (num_labels - 1)
            for i in range(num_labels):
                y = start_y + graph_height - int(i * step_y)
                temp_label = round(min_temp + (i / (num_labels - 1)) * temp_range, 1)
                if image4Gray:
                    self.epd.image4Gray.text(str(temp_label), start_x + 3, y - 10, self.epd.black)  # Отступ для текста
                else:
                    self.epd.image1Gray.text(str(temp_label), start_x + 3, y - 10, self.epd.black)  # Отступ для текста
        else:
            # Рисуем метки для оси Y (начало, середина и конец)
            for i, position in enumerate([0, 0.5, 1]):
                y = start_y + graph_height - int(position * graph_height)
                temp_label = round(min_temp + position * temp_range, 1)
                if image4Gray:
                    self.epd.image4Gray.text(str(temp_label), start_x + 3, y - 10, self.epd.black)  # Отступ для текста
                else:
                    self.epd.image1Gray.text(str(temp_label), start_x + 3, y - 10, self.epd.black)  # Отступ для текста
        
        # output the last value
        if image4Gray:
            self.epd.image4Gray.text(str(round(last_value, 1)), start_x + graph_width - 16 , start_y, self.epd.black)
        else:
            self.epd.image1Gray.text(str(round(last_value, 1)), start_x + graph_width, start_y + graph_height, self.epd.black)
        
    @staticmethod
    def format_time(utc_time, timezone_offset):
        try:
            #time_part = utc_time.split('T')[1].split('.')[0]
            time_part = utc_time.split('T')[1].split('Z')[0]
            time_part = time_part.split('.')[0]
            hours, minutes, seconds = map(int, time_part.split(':'))
            total_seconds = hours * 3600 + minutes * 60 + seconds + timezone_offset
            total_seconds %= 24 * 3600
            local_hours = total_seconds // 3600
            local_minutes = (total_seconds % 3600) // 60
            return f"{local_hours:02}:{local_minutes:02}"
        except Exception:
            return "--:--"
        
        
   
        
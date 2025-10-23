from machine import Pin, SPI
import time
import st7789py as st7789
from text_display import *
from influxdb_data import *

spi = SPI(1, baudrate=40000000, sck=Pin(7), mosi=Pin(6))

reset = Pin(21, Pin.OUT)
dc = Pin(15, Pin.OUT)
cs = Pin(14, Pin.OUT)
backlight = Pin(22, Pin.OUT)

tft = st7789.ST7789(spi, 172, 320, reset, dc, cs, backlight=backlight, xstart=34, ystart=0)
tft.init()

# Включаем подсветку
backlight.value(1)


font_display = FontDisplay(tft)

#font_display.draw_text("Hello World!", 20, 40, hallfetica_16x16, rotate=True)


query_temperature = "SELECT mean(\"value\") AS value FROM temp WHERE time > now() - 12h AND \"sensor\" = 'bme' AND \"location\" = 'inside' GROUP BY time(30m) ORDER BY time ASC"
query_pressure    = "SELECT mean(\"value\") AS value FROM pres WHERE time > now() - 24h AND \"sensor\" = 'bme' AND \"location\" = 'inside' GROUP BY time(40m) ORDER BY time ASC"

graph_data_temperature = GraphData(query_temperature)
graph_data_temperature.fetch_data(filtered=False)
graph_data_pressure = GraphData(query_pressure)
graph_data_pressure.fetch_data(filtered=False)
temperatures, timestamps = graph_data_temperature.get_scaled_data()
time.sleep(2)
pressure, timestamps_pres = graph_data_pressure.get_scaled_data()
pressure_rounded = [round(p, 2) for p in pressure]
print(graph_data_temperature.get_scaled_data())


font_display.draw_text("Hello World!", 20, 40, hallfetica_16x16, rotate=True)
# Отправляем буфер на экран
tft.blit_buffer(buffer, 0, 0, 172, 320)

time.sleep(5)  

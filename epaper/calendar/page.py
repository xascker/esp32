import utime
import gc
import ntptime
import machine 
from epd4in2v2 import EPD_4in2
from influxdb_data import *
from graphs import *
from calendar import CalendarDisplay
from battery import DrawBattery
from icon_display import *
from weather import GetWeather
from moon import MoonPhase

EPD_WIDTH = 400
EPD_HEIGHT = 300

def log_memory(step):
    print(f"Memory at {step}: {gc.mem_free()} bytes free")

log_memory("start")

def run_code():
    epd = EPD_4in2()
    epd.image4Gray.fill(0xff)
    epd.EPD_4IN2_V2_Init_4Gray()

    battery = DrawBattery(epd)
    battery.draw_battery(image4Gray=True)

    weather = GetWeather()
    weather.fetch_data()
    wind_speed = weather.get_wind_speed()
    wind_direction = weather.get_wind_direction()
    sunrise_time = weather.get_sunrise()
    sunset_time = weather.get_sunset()
    temp_internet = weather.get_temperature()
    humidity_internet = weather.get_humidity()
    
    icon_display = IconDisplay(epd)
    icon_display.draw_icon(250, 50, wind_32x32, image4Gray=True)
    icon_display.draw_icon(305, 50, sunrise_32x32, image4Gray=True)
    icon_display.draw_icon(360, 50, sunset_32x32, image4Gray=True)
    epd.image4Gray.text(wind_speed + 'm/s', 245, 85, epd.black)
    epd.image4Gray.text(sunrise_time, 305, 85, epd.black)
    epd.image4Gray.text(sunset_time, 360, 85, epd.black)
    epd.image4Gray.text(weather.wind_direction_to_cardinal(wind_direction), 265, 73, epd.darkgray)
    epd.image4Gray.text(temp_internet, 360, 105, epd.black)
    epd.image4Gray.text(humidity_internet, 360, 118, epd.black)
    gc.collect()
    log_memory("after weather")
    
    moon = MoonPhase(epd)
    moon.draw_moon_phase(260, 105, image4Gray=True)
    gc.collect()
    log_memory("after moon")
    
    calendar_display = CalendarDisplay(epd)
    calendar_display.draw_calendar(1,1)
    gc.collect()
    log_memory("after calendar")
        
    graph_width = 150
    graph_height = 80
    query_temperature = "SELECT mean(\"value\") AS value FROM temp WHERE time > now() - 12h AND \"sensor\" = 'bme' AND \"location\" = 'inside' GROUP BY time(30m) ORDER BY time ASC"
    query_pressure    = "SELECT mean(\"value\") AS value FROM pres WHERE time > now() - 24h AND \"sensor\" = 'bme' AND \"location\" = 'inside' GROUP BY time(40m) ORDER BY time ASC"

    graph_data_temperature = GraphData(query_temperature)
    graph_data_temperature.fetch_data(filtered=False)
    graph_data_pressure = GraphData(query_pressure)
    graph_data_pressure.fetch_data(filtered=False)
    temperatures, timestamps = graph_data_temperature.get_scaled_data()
    utime.sleep(2)
    pressure, timestamps_pres = graph_data_pressure.get_scaled_data()
    pressure_rounded = [round(p, 2) for p in pressure]

    gc.collect()
    log_memory("after influxdb query")
    
    drawer = GraphDrawer(epd)
    
    if temperatures and timestamps:
        drawer.draw_graph(temperatures, timestamps, 220, 190, graph_width, graph_height, show_all_labels=False, image4Gray=True)
    else:
        print("No data available to draw.")
    gc.collect()
    if pressure_rounded and timestamps_pres:
        drawer.draw_graph(pressure_rounded, timestamps_pres, 10, 190, graph_width, graph_height, show_all_labels=False, image4Gray=True)
    else:
        print("No data available to draw.")
    gc.collect()
    
    ntptime.settime()
    current_time = utime.localtime()
    utc_fetcher = GetUtc()
    local_utc = utc_fetcher.get_local_utc()
    hours = (current_time[3] + local_utc) % 24
    formatted_time = "{:02}:{:02}".format(hours, current_time[4])
    epd.image4Gray.text(formatted_time, 360, 292, epd.darkgray)
    gc.collect()   
    log_memory("the end")
    
    epd.EPD_4IN2_V2_4GrayDisplay(epd.buffer_4Gray)
    epd.delay_ms(5000)


# Основной цикл с глубоким сном
while True:
    run_code() 
    machine.deepsleep(10800000)  # 3 hour
    #machine.deepsleep(120000) # 3 min
    
    
    
    
    
    
    
    
    
    
    
    
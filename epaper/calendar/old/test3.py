import utime
from epd4in2v2 import EPD_4in2
from influxdb_data import *
from graphs import *

EPD_WIDTH = 400
EPD_HEIGHT = 300


if __name__ == '__main__':
    epd = EPD_4in2()
    epd.image1Gray.fill(0xff)
    epd.EPD_4IN2_V2_Init()
    
    # Размеры и положение графика
    #start_x = 200
    #start_y = 100
    graph_width = 150
    graph_height = 80
    
    
    query_temperature = "SELECT * FROM temp WHERE time > now() - 12h AND \"sensor\" = 'bme' AND \"location\" = 'inside'"
    query_pressure = "SELECT * FROM pres WHERE time > now() - 12h AND \"sensor\" = 'bme' AND \"location\" = 'inside'"
    
    graph_data_temperature = GraphData(query_temperature)
    graph_data_temperature.fetch_data()
    
    graph_data_pressure = GraphData(query_pressure)
    graph_data_pressure.fetch_data()
    
    temperatures, timestamps = graph_data_temperature.get_scaled_data()
    pressure, timestamps = graph_data_pressure.get_scaled_data()
    
    pressure_rounded = [round(p, 2) for p in pressure]
    
    print(temperatures)
    print(timestamps)
    print(pressure)
    print(timestamps)
    
    drawer = GraphDrawer(epd)
    
    if temperatures and timestamps:
        #drawer.draw_graph(data, timestamps, start_x, start_y, graph_width, graph_height, show_all_labels)
        drawer.draw_graph(temperatures, timestamps, 220, 180, graph_width, graph_height, show_all_labels=False, image4Gray=False)
    else:
        print("No data available to draw.")
        
    if pressure_rounded and timestamps:
        drawer.draw_graph(pressure_rounded, timestamps, 10, 180, graph_width, graph_height, show_all_labels=False, image4Gray=False)
    else:
        print("No data available to draw.")
        
    
    
    epd.EPD_4IN2_V2_Display(epd.buffer_1Gray)
    epd.delay_ms(5000) 
    epd.Sleep()
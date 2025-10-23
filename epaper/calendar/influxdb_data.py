import network
import urequests
import ujson

influxdb = "http://192.168.1.250:8086"
influxdb_name = 'meteo'

class GraphData:
    def __init__(self,query):
        self.influxdb_url = influxdb + "/query"
        self.query = query

        self.data = []
        self.timestamps = []
        
    wifi = network.WLAN(network.STA_IF)
    if wifi.isconnected():

        def fetch_data(self, filtered):
            try:
                full_url = self.influxdb_url + "?db=" + influxdb_name + "&q=" + self.url_encode(self.query)
                response = urequests.get(full_url)
                if response.status_code == 200:
                    data = ujson.loads(response.text)
                    #print(data)
                    values = data['results'][0]['series'][0]['values']
                    filtered_values = values[::2]
                    if filtered:
                        self.data = [float(item[3]) for item in filtered_values]
                        self.timestamps = [item[0] for item in filtered_values]
                    else:
                        #self.data = [float(item[1]) for item in values]
                        #self.timestamps = [item[0] for item in values]
                        self.data = [float(item[1]) for item in values if item[1] is not None]
                        self.timestamps = [item[0] for item in values if item[1] is not None]
                else:
                    print(f"Error fetching data: {response.status_code}")
                response.close()
            except Exception as e:
                print(f"Data processing error: {e}")

        @staticmethod
        def url_encode(string):
            return string.replace(' ', '%20').replace('"', '%22').replace("'", '%27')

        def get_scaled_data(self):
            #print('get_scaled_data')
            #print(self.data, self.timestamps)
            return self.data, self.timestamps
    
    else:
        print("The device is not connected to Wi-Fi network")

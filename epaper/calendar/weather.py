import ujson
import utime
import urequests
from set_utc import GetUtc

weather_url = "http://192.168.1.250/weather.php"

utc_fetcher = GetUtc()
local_utc = utc_fetcher.get_local_utc()
timezone_offset = round(local_utc * 3600)

class GetWeather:
    def __init__(self):
        self.url = weather_url
        self.data = None

    def fetch_data(self):
        try:
            response = urequests.get(self.url)
            if response.status_code == 200:
                self.data = ujson.loads(response.text)
            else:
                print("Request error, response code:", response.status_code)
        except Exception as e:
            print("Error executing request:", e)
        finally:
            if 'response' in locals():
                response.close()

    def get_wind_speed(self):
        if self.data:
            wind_speed = self.data.get('wind', {}).get('speed', None)
            if wind_speed is not None:
                #return str(round(wind_speed, 1))
                return (f"{wind_speed:.1f}")
        return None
    
    def get_wind_direction(self):
        if self.data:
            wind_deg = self.data.get('wind', {}).get('deg', None)
            if wind_deg is not None:
                return wind_deg
        return None
    
    def wind_direction_to_cardinal(self, degrees):
        if degrees is None:
            return None
        if 0 <= degrees < 22.5 or degrees >= 337.5:
            return "N"
        elif 22.5 <= degrees < 67.5:
            return "NE"
        elif 67.5 <= degrees < 112.5:
            return "E"
        elif 112.5 <= degrees < 157.5:
            return "SE"
        elif 157.5 <= degrees < 202.5:
            return "S"
        elif 202.5 <= degrees < 247.5:
            return "SW"
        elif 247.5 <= degrees < 292.5:
            return "W"
        elif 292.5 <= degrees < 337.5:
            return "NW"
        else:
            return "Unknown"

    def get_sunrise(self):
        if self.data:
            sunrise_epoch = self.data.get('sys', {}).get('sunrise', None)
            if sunrise_epoch:
                #return sunrise_epoch
                local_sunrise = self.convert_utc_to_local(sunrise_epoch)
                return self.format_time(local_sunrise)
        return None

    def get_sunset(self):
        if self.data:
            sunset_epoch = self.data.get('sys', {}).get('sunset', None)
            if sunset_epoch:
                #return sunset_epoch
                local_sunset = self.convert_utc_to_local(sunset_epoch)
                return self.format_time(local_sunset)
        return None
    
    def get_temperature(self):
        if self.data:
            temperature_epoch = self.data.get('main', {}).get('temp', None)
            if temperature_epoch:
                return (f"{temperature_epoch:.1f}")
        return None
    
    def get_humidity(self):
        if self.data:
            humidity_epoch = self.data.get('main', {}).get('humidity', None)
            if humidity_epoch:
                return ("{}%".format(humidity_epoch))
        return None

    def convert_utc_to_local(self, epoch_time):
        if isinstance(epoch_time, (int, float)):
            epoch_time = int(epoch_time) 
            local_time = epoch_time + timezone_offset
            return utime.localtime(local_time)
        else:
            print("Error: Non-numeric data type for time or offset.")
            return None

    @staticmethod
    def format_time(local_time):
        return "{:02}:{:02}".format(local_time[3], local_time[4], local_time[5])




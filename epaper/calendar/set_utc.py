import network
import urequests


class GetUtc:
    def __init__(self):
        self.wifi = network.WLAN(network.STA_IF)

    def get_local_utc(self):
        if self.wifi.isconnected():
            try:
                # Запрашиваем данные с API
                response = urequests.get("http://worldtimeapi.org/api/ip")
                data = response.json()

                # Извлекаем смещение от UTC
                utc_offset = data["utc_offset"]  # Формат: "+03:00" или "-07:00"
                hours, minutes = map(int, utc_offset[1:].split(":"))

                # Преобразуем смещение в часы
                offset_hours = hours + minutes / 60
                if utc_offset[0] == "-":
                    offset_hours = -offset_hours

                return offset_hours
            except Exception as e:
                print("Error determining time zone:", e)
                return None
        else:
            print("The device is not connected to Wi-Fi network")
            return None


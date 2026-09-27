import network
import time
import ntptime

SSID = '123'
PASSWORD = '123'

wifi = network.WLAN(network.STA_IF)
wifi.active(True)


def connect_wifi(max_attempts=10):
    if wifi.isconnected():
        print('Already connected! IP:', wifi.ifconfig()[0])
        return True

    print('Connecting to Wi-Fi:', SSID)

    wifi.connect(SSID, PASSWORD)

    attempt = 0

    while not wifi.isconnected() and attempt < max_attempts:
        attempt += 1
        print(f'Connecting to Wi-Fi... attempt {attempt}')
        time.sleep(2)

    if wifi.isconnected():
        print('Connected! IP:', wifi.ifconfig()[0])
        return True

    print('Failed to connect.')
    return False


def sync_time():
    try:
        ntptime.settime()
        print("Time synchronized via NTP")
    except:
        print("Failed to sync time")
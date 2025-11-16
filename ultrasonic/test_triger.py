from hc_sr04 import HCSR04
import time

THRESHOLD = 10  # cm

sensor = HCSR04(trigger_pin=5, echo_pin=19)

while True:
    d = sensor.distance_cm()

    if d is not None and d <= THRESHOLD:
        print("ALERT:", d, "cm")

    time.sleep(0.5)
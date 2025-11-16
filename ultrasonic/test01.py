from hc_sr04 import HCSR04
import time

sensor = HCSR04(trigger_pin=5, echo_pin=19)

while True:
    d = sensor.distance_cm()
    if d is not None:
        print("Distance:", d, "cm")
    else:
        print("No echo")
    time.sleep(0.5)
    
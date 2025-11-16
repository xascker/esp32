from machine import Pin, time_pulse_us
import time

class HCSR04:
    def __init__(self, trigger_pin, echo_pin, timeout=30000):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.timeout = timeout

    def distance_cm(self):
        self.trigger.off()
        time.sleep_us(2)

        self.trigger.on()
        time.sleep_us(10)
        self.trigger.off()

        duration = time_pulse_us(self.echo, 1, self.timeout)
        if duration <= 0:
            return None

        distance = (duration * 0.0343) / 2
        return round(distance, 1)
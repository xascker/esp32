from machine import Pin
import neopixel
import time

# --- Color definitions ---
RED     = (255, 0,   0)
GREEN   = (0,   255, 0)
BLUE    = (0,   0,   255)
WHITE   = (255, 255, 255)
YELLOW  = (255, 255, 0)
CYAN    = (0,   255, 255)
MAGENTA = (255, 0,   255)
BLACK   = (0,   0,   0)

# --- LED strip configuration ---
NUM_LED = 299        # number of LEDs | 5m = 300 -1
PIN_NUM = 18       # GPIO pin for DIN

BRIGHTNESS = 0.05 # 0.0 to 1.0

np = neopixel.NeoPixel(Pin(PIN_NUM), NUM_LED)
COLOR = MAGENTA

# --- Helper function to apply brightness ---
def apply_brightness(color, brightness):
    r, g, b = color
    return (int(r * brightness), int(g * brightness), int(b * brightness))

# --- Light LEDs one by one ---
for i in range(NUM_LED):

    # turn current LED on (red)
    np[i] = apply_brightness(COLOR, BRIGHTNESS)
    np.write()
    time.sleep(0.02)

    # turn off only if it's not the last LED
    if i < NUM_LED - 1:
        np[i] = BLACK
        np.write()

# --- Blink the last LED forever ---
last = NUM_LED - 1

while True:
    # turn on last LED
    np[last] = apply_brightness(COLOR, BRIGHTNESS)
    np.write()
    time.sleep(0.3)

    # turn it off
    np[last] = BLACK
    np.write()
    time.sleep(0.3)
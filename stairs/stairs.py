import time
import _thread
from machine import Pin
from machine import Timer
import neopixel
import json
from hc_sr04 import HCSR04

"""
Ultrasonic sensors:
sensor_01_device:
    TRIGGER - GPIO5
    ECHO    - GPIO19

sensor_02_device:
    TRIGGER - GPIO17
    ECHO    - GPIO16

LED strip (NeoPixel):
    PIN_NUM - GPIO18 
"""

sensor_01_device = HCSR04(trigger_pin=5, echo_pin=19)
sensor_02_device = HCSR04(trigger_pin=17, echo_pin=16)

# ---------- COLORS ----------
RED     = (255,   0,   0)
GREEN   = (0,   255,   0)
BLUE    = (0,     0, 255)
WHITE   = (255, 255, 255)
YELLOW  = (255, 255,   0)
CYAN    = (0,   255, 255)
MAGENTA = (255,   0, 255)
BLACK   = (0,     0,   0)

# ---------- DEFAULT SETTINGS ----------
SETTINGS_FILE = "settings.json"

NUM_STAIRS = 10
LED_BLOCK = 4
NUM_LED = NUM_STAIRS * LED_BLOCK

PIN_NUM = 18
BRIGHTNESS = 0.05
COLOR = CYAN
COLOR_NAME = "CYAN"

ANIMATION_SPEED = 0.1
AUTO_OFF_DELAY = 20
SENSOR_FADE_DELAY = 20

THRESHOLD = 10 

# ---------- LOAD / SAVE SETTINGS ----------
def load_settings():
    global NUM_STAIRS, LED_BLOCK, NUM_LED
    global BRIGHTNESS, COLOR, COLOR_NAME, THRESHOLD
    global ANIMATION_SPEED, AUTO_OFF_DELAY, SENSOR_FADE_DELAY

    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)

        NUM_STAIRS = data.get("NUM_STAIRS", NUM_STAIRS)
        LED_BLOCK = data.get("LED_BLOCK", LED_BLOCK)
        NUM_LED = NUM_STAIRS * LED_BLOCK

        BRIGHTNESS = data.get("BRIGHTNESS", BRIGHTNESS)
        COLOR_NAME = data.get("COLOR_NAME", COLOR_NAME).upper()

        ANIMATION_SPEED = data.get("ANIMATION_SPEED", ANIMATION_SPEED)
        AUTO_OFF_DELAY = data.get("AUTO_OFF_DELAY", AUTO_OFF_DELAY)
        SENSOR_FADE_DELAY = data.get("SENSOR_FADE_DELAY", SENSOR_FADE_DELAY)
        THRESHOLD = data.get("THRESHOLD", THRESHOLD)

        # Map color name → RGB
        COLOR = {
            "RED": RED,
            "GREEN": GREEN,
            "BLUE": BLUE,
            "WHITE": WHITE,
            "YELLOW": YELLOW,
            "CYAN": CYAN,
            "MAGENTA": MAGENTA
        }.get(COLOR_NAME, CYAN)

    except Exception as e:
        print("Settings load error:", e)

def save_settings():
    data = {
        "NUM_STAIRS": NUM_STAIRS,
        "LED_BLOCK": LED_BLOCK,
        "BRIGHTNESS": BRIGHTNESS,
        "COLOR_NAME": COLOR_NAME,
        "ANIMATION_SPEED": ANIMATION_SPEED,
        "AUTO_OFF_DELAY": AUTO_OFF_DELAY,
        "SENSOR_FADE_DELAY": SENSOR_FADE_DELAY,
        "THRESHOLD": THRESHOLD
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print("Settings save error:", e)

# ---------- BRIGHTNESS ----------
def apply_brightness(col, brightness):
    r, g, b = col
    return (int(r * brightness), int(g * brightness), int(b * brightness))

# ---------- INITIALIZE LED STRIP ----------
load_settings()
np = neopixel.NeoPixel(Pin(PIN_NUM), NUM_LED)


# ----------
is_strip_on = False
fade_thread_running = False
auto_off_timer = None
led_state = [(0,0,0)] * NUM_LED
sensor_01_state = False
sensor_02_state = False

def start_auto_off_timer():
    global auto_off_timer, is_strip_on
    if AUTO_OFF_DELAY <= 0 or not is_strip_on:
        return

    # cancel old timer if exists
    if auto_off_timer is not None:
        auto_off_timer.deinit()
        auto_off_timer = None

    # create new one-shot timer
    auto_off_timer = Timer(0) 
    auto_off_timer.init(
        period=AUTO_OFF_DELAY*1000,
        mode=Timer.ONE_SHOT,
        callback=lambda t: fade_out_wrapper()
    )
    
def fade_out_wrapper():
    global is_strip_on, auto_off_timer
    if not is_strip_on:
        return

    fade_out()
    is_strip_on = False

    if auto_off_timer is not None:
        auto_off_timer.deinit()
        auto_off_timer = None

def fade_out():
    global np, sensor_01_state, sensor_02_state
    steps = 50  # number of fade steps
    sensor_01_state = False
    sensor_02_state = False
    for step in range(steps, 0, -1):
        factor = step / steps
        for i in range(NUM_LED):
            r, g, b = COLOR
            np[i] = (int(r * BRIGHTNESS * factor),
                     int(g * BRIGHTNESS * factor),
                     int(b * BRIGHTNESS * factor))
        np.write()
        time.sleep(0.04)

    for i in range(NUM_LED):
        np[i] = (0,0,0)
    np.write()
    
def light_leds_block():
    global led_state, is_strip_on, auto_off_timer
    
    if auto_off_timer is not None:
        auto_off_timer.deinit()
        auto_off_timer = None
        
    for stair in range(NUM_STAIRS):
        start = stair * LED_BLOCK
        end = start + LED_BLOCK
        for i in range(start, end):
            if i < NUM_LED:
                led_state[i] = apply_brightness(COLOR, BRIGHTNESS)
                np[i] = led_state[i]
        np.write()
        time.sleep(ANIMATION_SPEED)
    is_strip_on = True
    start_auto_off_timer()
    
def light_leds_block_reverse():
    global led_state, is_strip_on, auto_off_timer
    
    if auto_off_timer is not None:
        auto_off_timer.deinit()
        auto_off_timer = None
        
    for stair in range(NUM_STAIRS-1, -1, -1):
        start = stair * LED_BLOCK
        end = start + LED_BLOCK
        for i in range(start, end):
            if i < NUM_LED:
                led_state[i] = apply_brightness(COLOR, BRIGHTNESS)
                np[i] = led_state[i]
        np.write()
        time.sleep(ANIMATION_SPEED)
    is_strip_on = True
    start_auto_off_timer()
        
def fade_off_blockwise():
    global led_state, is_strip_on
    is_strip_on = False
    for stair in range(NUM_STAIRS):
        start = stair * LED_BLOCK
        end = start + LED_BLOCK
        # create a temporary buffer
        temp_np = [led_state[i] for i in range(NUM_LED)]
        # we off only the current block
        for i in range(start, end):
            if i < NUM_LED:
                temp_np[i] = (0,0,0)
                led_state[i] = (0,0,0)  # updating the main state

        # write the buffer to strip
        for i in range(NUM_LED):
            np[i] = temp_np[i]

        np.write()
        time.sleep(ANIMATION_SPEED) 
        
def fade_off_blockwise_reverse():
    global led_state, is_strip_on
    is_strip_on = False
    for stair in range(NUM_STAIRS-1, -1, -1): 
        start = stair * LED_BLOCK
        end = start + LED_BLOCK

        for i in range(start, end):
            if i < NUM_LED:
                led_state[i] = (0,0,0)

        for i in range(NUM_LED):
            np[i] = led_state[i]
            
        np.write()
        time.sleep(ANIMATION_SPEED)
# ----------
# ---------- Sensors logic ----------

def sensor_01():
    global sensor_01_state, sensor_02_state, is_strip_on, fade_thread_02_running
    
    if is_strip_on == "PROCESSING":
        return
    
    if sensor_02_state and is_strip_on:
        is_strip_on = "PROCESSING"
        sensor_02_state = False
        _thread.start_new_thread(_delayed_fade, (fade_off_blockwise_reverse, SENSOR_FADE_DELAY)) # Don't turn it off right away, let others pass if there are a lot of people
        #fade_off_blockwise_reverse()
    else:
        if not is_strip_on:
            sensor_01_state = True
            light_leds_block()
    
def sensor_02():
    global sensor_01_state, sensor_02_state, is_strip_on, fade_thread_01_running
    
    if is_strip_on == "PROCESSING":
        return
    
    if sensor_01_state and is_strip_on:
        is_strip_on = "PROCESSING"
        sensor_01_state = False
        _thread.start_new_thread(_delayed_fade, (fade_off_blockwise, SENSOR_FADE_DELAY))
        #fade_off_blockwise()
    else:
        if not is_strip_on:
            sensor_02_state = True
            light_leds_block_reverse()


def _delayed_fade(func, delay=20):
    global is_strip_on
    time.sleep(delay)
    func()
    is_strip_on = False
    
# ----------    
# ---------- Sensor devices ----------    


def sensor_loop_01():
    while True:
        d = sensor_01_device.distance_cm()
        if d is not None and d <= THRESHOLD:
            sensor_01()
        time.sleep(0.2)

def sensor_loop_02():
    while True:
        d = sensor_02_device.distance_cm()
        if d is not None and d <= THRESHOLD:
            sensor_02()
        time.sleep(0.2)

#_thread.start_new_thread(sensor_loop_01, ())
#_thread.start_new_thread(sensor_loop_02, ())

# ----------
def start():
    
    # --- Test LED strip once at startup ---
    light_leds_block()
    time.sleep(0.5)
    fade_off_blockwise()

    # --- start sensor threads ---
    _thread.start_new_thread(sensor_loop_01, ())
    _thread.start_new_thread(sensor_loop_02, ())


    






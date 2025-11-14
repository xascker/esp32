import time
import _thread
from machine import Pin
import neopixel
import json

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

# ---------- LOAD / SAVE SETTINGS ----------
def load_settings():
    global NUM_STAIRS, LED_BLOCK, NUM_LED
    global BRIGHTNESS, COLOR, COLOR_NAME
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
        "SENSOR_FADE_DELAY": SENSOR_FADE_DELAY
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
auto_off_enabled = False
led_state = [(0,0,0)] * NUM_LED
sensor_01_state = False
sensor_02_state = False

def start_auto_off_timer():
    global fade_thread_running
    if AUTO_OFF_DELAY <= 0:
        return
    if fade_thread_running:
        return
    fade_thread_running = True
    try:
        _thread.start_new_thread(_schedule_fade, ())
    except Exception as e:
        print("Failed to start fade thread:", e)

def _schedule_fade():
    """Fade out LEDs after AUTO_OFF_DELAY seconds."""
    global fade_thread_running, is_strip_on
    time.sleep(AUTO_OFF_DELAY)
    if is_strip_on:
        fade_out()     
        is_strip_on = False
    fade_thread_running = False
    
def light_leds_block():
    global led_state, is_strip_on
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
    global led_state, is_strip_on
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
        # создаём временный буфер
        temp_np = [led_state[i] for i in range(NUM_LED)]
        # гасим только текущий блок
        for i in range(start, end):
            if i < NUM_LED:
                temp_np[i] = (0,0,0)
                led_state[i] = (0,0,0)  # обновляем основное состояние

        # записываем буфер на ленту
        for i in range(NUM_LED):
            np[i] = temp_np[i]

        np.write()
        time.sleep(ANIMATION_SPEED) 
        
def fade_off_blockwise_reverse():
    global led_state, is_strip_on
    is_strip_on = False
    for stair in range(NUM_STAIRS-1, -1, -1):  # обратный порядок
        start = stair * LED_BLOCK
        end = start + LED_BLOCK

        for i in range(start, end):
            if i < NUM_LED:
                led_state[i] = (0,0,0)

        for i in range(NUM_LED):
            np[i] = led_state[i]
            
        np.write()
        time.sleep(ANIMATION_SPEED)

def fade_out():
    """Smooth fade out of the whole LED strip."""
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

    # final off
    for i in range(NUM_LED):
        np[i] = (0,0,0)
    np.write()
# ----------
# ---------- Sensors ----------

def sensor_01():
    global sensor_01_state, sensor_02_state, is_strip_on
    if sensor_02_state:
        sensor_02_state = False
        _thread.start_new_thread(_delayed_fade, (fade_off_blockwise_reverse, SENSOR_FADE_DELAY)) # Don't turn it off right away, let others pass if there are a lot of people
        #fade_off_blockwise_reverse()
    else:
        if is_strip_on == False:
            sensor_01_state = True
            light_leds_block()
    
def sensor_02():
    global sensor_01_state, sensor_02_state, is_strip_on
    if sensor_01_state:
        sensor_01_state = False
        _thread.start_new_thread(_delayed_fade, (fade_off_blockwise, SENSOR_FADE_DELAY))
        #fade_off_blockwise()
    else:
        if is_strip_on == False:
            sensor_02_state = True
            light_leds_block_reverse()


def _delayed_fade(func, delay=20):
    global is_strip_on
    is_strip_on = False
    time.sleep(delay)
    func()
# ----------
    
#light_leds_block()
#time.sleep(0.5)
#fade_off_blockwise() 

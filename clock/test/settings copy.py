import ujson

FILENAME = "clock_settings.json"

display_brightness = 0
TIMEZONE_OFFSET = -6

def load_settings():
    global display_brightness, TIMEZONE_OFFSET
    try:
        with open(FILENAME, "r") as f:
            data = ujson.load(f)
            display_brightness = data.get("brightness", 0)
            TIMEZONE_OFFSET = data.get("timezone", -6)
    except:
        display_brightness = 0
        TIMEZONE_OFFSET = -6

def save_settings():
    global display_brightness, TIMEZONE_OFFSET
    try:
        with open(FILENAME, "w") as f:
            ujson.dump({"brightness": display_brightness, "timezone": TIMEZONE_OFFSET}, f)
    except:
        pass
import ujson

display_brightness = 2
TIMEZONE_OFFSET = -6
SCROLL_SPEED = 0.05
ANIMATION_DELAY = 0.1

SETTINGS_FILE = "settings.json"

def save_settings():
    global display_brightness, TIMEZONE_OFFSET, SCROLL_SPEED, ANIMATION_DELAY
    try:
        with open(SETTINGS_FILE, "w") as f:
            ujson.dump({
                "display_brightness": display_brightness,
                "TIMEZONE_OFFSET": TIMEZONE_OFFSET,
                "SCROLL_SPEED": SCROLL_SPEED,
                "ANIMATION_DELAY": ANIMATION_DELAY 
            }, f)
        print("Settings saved.")
    except Exception as e:
        print("Error saving settings:", e)

def load_settings():
    global display_brightness, TIMEZONE_OFFSET, SCROLL_SPEED, ANIMATION_DELAY 
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = ujson.load(f)
        display_brightness = data.get("display_brightness", display_brightness)
        TIMEZONE_OFFSET = data.get("TIMEZONE_OFFSET", TIMEZONE_OFFSET)
        SCROLL_SPEED = data.get("SCROLL_SPEED", SCROLL_SPEED)
        ANIMATION_DELAY = data.get("ANIMATION_DELAY", ANIMATION_DELAY) 
        print("Settings loaded.")
    except Exception as e:
        print("No settings file found, using defaults.")

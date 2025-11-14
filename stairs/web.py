import socket
import time
import stairs
import _thread



# --- Mapping color names to RGB ---
COLOR_MAP = {
    "red": stairs.RED,
    "green": stairs.GREEN,
    "blue": stairs.BLUE,
    "cyan": stairs.CYAN,
    "yellow": stairs.YELLOW,
    "magenta": stairs.MAGENTA,
    "white": stairs.WHITE
}

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print("Web server running on", addr)        
            
while True:
    cl, addr = s.accept()
    print("Client connected:", addr)

    request = cl.recv(1024).decode()

    action = None  # update / animate

    # ---------- Parse GET params ----------
    if "/?" in request:
        try:
            params = request.split("/?")[1].split(" ")[0]
            kv_pairs = params.split("&")

            for kv in kv_pairs:
                if "=" not in kv:
                    continue
                key, value = kv.split("=")
                key = key.lower()
                value = value.lower()

                # ACTIONS
                if key == "action":
                    action = value  # update / animate

                # SETTINGS
                elif key == "color" and value in COLOR_MAP:
                    stairs.COLOR = COLOR_MAP[value]
                    stairs.COLOR_NAME = value.upper()

                elif key == "brightness":
                    stairs.BRIGHTNESS = float(value)

                elif key == "stairs":
                    stairs.NUM_STAIRS = int(value)
                    stairs.NUM_LED = stairs.NUM_STAIRS * stairs.LED_BLOCK
                    stairs.np = stairs.neopixel.NeoPixel(
                        stairs.Pin(stairs.PIN_NUM), stairs.NUM_LED
                    )

                elif key == "block":
                    stairs.LED_BLOCK = int(value)
                    stairs.NUM_LED = stairs.NUM_STAIRS * stairs.LED_BLOCK
                    stairs.np = stairs.neopixel.NeoPixel(
                        stairs.Pin(stairs.PIN_NUM), stairs.NUM_LED
                    )

                elif key == "speed":
                    stairs.ANIMATION_SPEED = float(value)

                elif key == "auto_off":
                    stairs.AUTO_OFF_DELAY = int(value)
                
                elif key == "sensor_delay":
                    stairs.SENSOR_FADE_DELAY = int(value)

        except Exception as e:
            print("Parse error:", e)

    # ---------- ACTION HANDLING ----------
    if action == "update":
        stairs.save_settings()

    elif action == "animate_forward":
        stairs.light_leds_block()

    elif action == "animate_reverse":
        stairs.light_leds_block_reverse()

    elif action == "fade_off_forward":
        stairs.fade_off_blockwise()
        
    elif action == "fade_off_forward_reverse":
        stairs.fade_off_blockwise_reverse()
        
    elif action == "sensor_01":
        stairs.sensor_01()
    
    elif action == "sensor_02":
        stairs.sensor_02()
    

    # ---------- COLOR SELECTED STATE ----------
    color_upper = stairs.COLOR_NAME.upper()

    selected = {
        name: ("selected" if color_upper == name.upper() else "")
        for name in COLOR_MAP.keys()
    }

    # ---------- HTML PAGE ----------
    response = """HTTP/1.0 200 OK

<html>
<head><title>LED Stairs Control</title></head>
<body>
<h2>LED Stairs Controller</h2>

<form action="/" method="get">

<label>Color:</label>
<select name="color">
    <option value="red" {red}>Red</option>
    <option value="green" {green}>Green</option>
    <option value="blue" {blue}>Blue</option>
    <option value="cyan" {cyan}>Cyan</option>
    <option value="yellow" {yellow}>Yellow</option>
    <option value="magenta" {magenta}>Magenta</option>
    <option value="white" {white}>White</option>
</select><br><br>

<label>Brightness (0-1):</label>
<input type="text" name="brightness" value="{brightness}"><br><br>

<label>Number of stairs:</label>
<input type="text" name="stairs" value="{stairs}"><br><br>

<label>LED per stair:</label>
<input type="text" name="block" value="{block}"><br><br>

<label>Animation speed (sec):</label>
<input type="text" name="speed" value="{speed}"><br><br>

<label>Sensor off delay (sec):</label>
<input type="text" name="sensor_delay" value="{sensor_delay}"><br><br>

<label>Auto-off delay (sec):</label>
<input type="text" name="auto_off" value="{auto_off}"><br><br>

<button type="submit" name="action" value="update">Update</button><br><br>

<button type="submit" name="action" value="animate_forward">Animate_forward</button>
<button type="submit" name="action" value="fade_off_forward">Fade_off_forward</button>
<button type="submit" name="action" value="animate_reverse">Animate_reverse</button>
<button type="submit" name="action" value="fade_off_forward_reverse">Fade_off_forward_reverse</button><br><br>

<button type="submit" name="action" value="sensor_01">sensor_01</button>
<button type="submit" name="action" value="sensor_02">sensor_02</button>

</form>

<h3>Current settings:</h3>
<ul>
<li>Color: {color}</li>
<li>Brightness: {brightness}</li>
<li>Stairs: {stairs}</li>
<li>LED per stair: {block}</li>
<li>Animation speed: {speed}</li>
<li>Sensor off delay: {sensor_delay} sec</li>
<li>Auto-off delay: {auto_off} sec</li>
<li>Total LEDs: {num_led}</li>
</ul>

</body>
</html>
""".format(
        red=selected["red"],
        green=selected["green"],
        blue=selected["blue"],
        cyan=selected["cyan"],
        yellow=selected["yellow"],
        magenta=selected["magenta"],
        white=selected["white"],
        color=stairs.COLOR_NAME,
        brightness=stairs.BRIGHTNESS,
        stairs=stairs.NUM_STAIRS,
        block=stairs.LED_BLOCK,
        num_led=stairs.NUM_STAIRS * stairs.LED_BLOCK,
        speed=stairs.ANIMATION_SPEED,
        auto_off=stairs.AUTO_OFF_DELAY,
        sensor_delay=stairs.SENSOR_FADE_DELAY
        
    )

    cl.send(response)
    cl.close()

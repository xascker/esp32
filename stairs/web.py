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

def start():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print("Web server running on", addr)

    while True:
        cl, addr = s.accept()
        # print("Client connected:", addr)
        request = cl.recv(1024).decode()
        action = None

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

                    if key == "action":
                        action = value
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
                    elif key == "threshold":
                        stairs.THRESHOLD = int(value)

            except Exception as e:
                print("Parse error:", e)

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

        # Prepare HTML UI
        color_upper = stairs.COLOR_NAME.upper()
        selected = {
            name: ("selected" if color_upper == name.upper() else "")
            for name in COLOR_MAP.keys()
        }

        response = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n" + """\
<html>
<head>
<title>LED Stairs Control</title>
<style>
  body {{
    font-family: Arial, Helvetica, sans-serif;
    background: #111;
    color: #eaeaea;
    margin: 0;
    padding: 20px;
  }}
  h2, h3 {{
    text-align: center;
    margin-bottom: 16px;
  }}
  form {{
    width: 100%;
    max-width: 680px;
    margin: auto;
    background: #1b1b1b;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 0 10px #0006;
  }}
  .settings-table {{
    width: 100%;
    border-collapse: collapse;
  }}
  .settings-table td {{
    padding: 8px 10px;
    vertical-align: middle;
  }}
  .settings-table td.label {{
    width: 45%;
    text-align: right;
    font-weight: bold;
    padding-right: 12px;
  }}
  .settings-table td.input {{
    width: 55%;
  }}
  .settings-table input[type="text"],
  .settings-table select {{
    width: 100%;
    padding: 6px 8px;
    border: 1px solid #444;
    border-radius: 6px;
    background: #222;
    color: #eee;
  }}
  .btn {{
    margin: 6px 4px;
    padding: 10px 14px;
    font-size: 15px;
    font-weight: bold;
    border-radius: 6px;
    cursor: pointer;
    border: none;
    color: #fff;
    background: #0066cc;
  }}
  .btn.red {{ background: #cc0000; }}
  .btn.green {{ background: #2e8b57; }}
  .btn.orange {{ background: #ff8800; }}
  .btn:hover {{ opacity: 0.85; }}
  .center {{ text-align: center; }}
  .status-box {{
    width: 100%;
    max-width: 680px;
    margin: 20px auto;
    background: #1b1b1b;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 0 10px #0006;
  }}
  ul li {{ margin: 6px 0; }}
</style>
</head>

<body>
<h2>LED Stairs Controller</h2>

<form action="/" method="get">
<table class="settings-table">
  <tr>
    <td class="label">Color:</td>
    <td class="input">
      <select name="color">
        <option value="red" {red}>Red</option>
        <option value="green" {green}>Green</option>
        <option value="blue" {blue}>Blue</option>
        <option value="cyan" {cyan}>Cyan</option>
        <option value="yellow" {yellow}>Yellow</option>
        <option value="magenta" {magenta}>Magenta</option>
        <option value="white" {white}>White</option>
      </select>
    </td>
  </tr>
  <tr><td class="label">Brightness (0-1):</td><td class="input"><input type="text" name="brightness" value="{brightness}"></td></tr>
  <tr><td class="label">Stairs count:</td><td class="input"><input type="text" name="stairs" value="{stairs}"></td></tr>
  <tr><td class="label">LED per stair:</td><td class="input"><input type="text" name="block" value="{block}"></td></tr>
  <tr><td class="label">Animation speed (sec):</td><td class="input"><input type="text" name="speed" value="{speed}"></td></tr>
  <tr><td class="label">Threshold (cm):</td><td class="input"><input type="text" name="threshold" value="{threshold}"></td></tr>
  <tr><td class="label">Sensor delay (sec):</td><td class="input"><input type="text" name="sensor_delay" value="{sensor_delay}"></td></tr>
  <tr><td class="label">Auto-off delay (sec):</td><td class="input"><input type="text" name="auto_off" value="{auto_off}"></td></tr>
  <tr><td colspan="2" class="center"><button class="btn green" type="submit" name="action" value="update">Update Settings</button></td></tr>
  <tr><td colspan="2" class="center">
      <button class="btn" type="submit" name="action" value="animate_forward">Animate Forward</button>
      <button class="btn" type="submit" name="action" value="animate_reverse">Animate Reverse</button>
      <button class="btn" type="submit" name="action" value="fade_off_forward">Fade Off Forward</button>
      <button class="btn" type="submit" name="action" value="fade_off_forward_reverse">Fade Off Reverse</button>
  </td></tr>
  <tr><td colspan="2" class="center">
      <button class="btn red" type="submit" name="action" value="sensor_01">Trigger Sensor 1</button>
      <button class="btn red" type="submit" name="action" value="sensor_02">Trigger Sensor 2</button>
  </td></tr>
</table>
</form>

<div class="status-box">
  <h3>Current settings</h3>
  <ul>
    <li>Color: {color}</li>
    <li>Brightness: {brightness}</li>
    <li>Stairs: {stairs}</li>
    <li>LED per stair: {block}</li>
    <li>Animation speed: {speed} sec</li>
    <li>Threshold: {threshold} cm</li>
    <li>Sensor off delay: {sensor_delay} sec</li>
    <li>Auto-off delay: {auto_off} sec</li>
    <li>Total LEDs: {num_led}</li>
  </ul>
</div>

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
            sensor_delay=stairs.SENSOR_FADE_DELAY,
            threshold=stairs.THRESHOLD
        )

        cl.send(response)
        cl.close()
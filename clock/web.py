import usocket as socket
import uasyncio as asyncio
import mclock

HTML = """<!DOCTYPE html>
<html>
<head>
<title>ESP32 Clock Control</title>
<style>
  body {{
    font-family: Arial, Helvetica, sans-serif;
    background: #111;
    color: #eaeaea;
    margin: 0;
    padding: 20px;
  }}

  h1 {{
    text-align: center;
    margin-bottom: 20px;
  }}

  form {{
    width: 100%;
    max-width: 480px;
    margin: auto;
    background: #1b1b1b;
    padding: 20px;
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
    width: 50%;
    text-align: right;
    font-weight: bold;
    padding-right: 12px;
  }}

  .settings-table td.input {{
    width: 50%;
  }}

  .settings-table input[type="number"] {{
    width: 100%;
    padding: 6px 8px;
    border: 1px solid #444;
    border-radius: 6px;
    background: #222;
    color: #eee;
  }}

  input[type="submit"] {{
    margin-top: 12px;
    padding: 10px 16px;
    font-size: 15px;
    font-weight: bold;
    border-radius: 6px;
    cursor: pointer;
    border: none;
    color: #fff;
    background: #0066cc;
    width: 100%;
  }}

  input[type="submit"]:hover {{
    opacity: 0.85;
  }}

  .status-box {{
    width: 100%;
    max-width: 480px;
    margin: 20px auto;
    background: #1b1b1b;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 0 10px #0006;
  }}

  .status-box p {{
    margin: 6px 0;
  }}
</style>
</head>

<body>
<h1>ESP32 Clock Control</h1>

<form method="GET">
<table class="settings-table">
  <tr>
    <td class="label">Brightness (0-7):</td>
    <td class="input"><input type="number" name="brightness" min="0" max="7" value="{brightness}"></td>
  </tr>
  <tr>
    <td class="label">Timezone (-12..14):</td>
    <td class="input"><input type="number" name="timezone" min="-12" max="14" value="{timezone}"></td>
  </tr>
  <tr>
    <td class="label">Animation Delay (0.05..0.5):</td>
    <td class="input"><input type="number" step="0.01" name="animation" min="0.05" max="0.5" value="{animation}"></td>
  </tr>
  <tr>
    <td class="label">Scroll Speed (0.01..0.2):</td>
    <td class="input"><input type="number" step="0.01" name="scroll" min="0.01" max="0.2" value="{scroll}"></td>
  </tr>
</table>

<input type="submit" value="Apply">
</form>

<div class="status-box">
<p>Current Brightness: {brightness}</p>
<p>Current Timezone: {timezone}</p>
<p>Animation Delay: {animation}</p>
<p>Scroll Speed: {scroll}</p>
</div>

</body>
</html>
"""

async def handle_client(client):
    try:
        client.setblocking(False)
        request = b""
        for _ in range(10):
            try:
                chunk = client.recv(1024)
                if chunk:
                    request += chunk
                else:
                    break
            except:
                await asyncio.sleep(0.01)

        if not request:
            client.close()
            return

        try:
            first_line = request.split(b'\r\n')[0]
            path = first_line.split()[1].decode()
            if '?' in path:
                _, query = path.split('?', 1)
                params = dict(kv.split('=') for kv in query.split('&') if '=' in kv)
                if 'brightness' in params:
                    mclock.set_brightness(int(params['brightness']))
                if 'timezone' in params:
                    mclock.set_timezone(int(params['timezone']))
                if 'animation' in params:
                    mclock.set_animation_delay(float(params['animation']))
                if 'scroll' in params:
                    mclock.set_scroll_speed(float(params['scroll']))
        except Exception as e:
            print("Error parsing query:", e)

        client.send(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
        client.send(HTML.format(
            brightness=mclock.get_brightness(),
            timezone=mclock.get_timezone(),
            animation=mclock.get_animation_delay(),
            scroll=mclock.get_scroll_speed()
        ).encode())
    finally:
        client.close()

async def server_loop():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(5)
    s.setblocking(False)
    print("Listening on port 80...")

    while True:
        try:
            client, addr = s.accept()
            print("Client connected from", addr)
            asyncio.create_task(handle_client(client))
        except:
            await asyncio.sleep(0.05)
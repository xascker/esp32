import usocket as socket
import uasyncio as asyncio
import mclock

HTML = """<!DOCTYPE html>
<html>
<body>
<h1>ESP32 Clock Control</h1>
<form method="GET">
Brightness (0-7): <input type="number" name="brightness" min="0" max="7" value="{brightness}">
<br><br>
Timezone (-12..14): <input type="number" name="timezone" min="-12" max="14" value="{timezone}">
<br><br>
<input type="submit" value="Apply">
</form>
<br><br>
<p>Current Brightness: {brightness}</p>
<p>Current Timezone: {timezone}</p>
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
        except:
            pass

        client.send(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
        client.send(HTML.format(
            brightness=mclock.get_brightness(),
            timezone=mclock.get_timezone()
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

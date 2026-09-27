import network
import socket


SETUP_SSID = "Clock-Setup"
SETUP_PASSWORD = "12345678"

CONFIG_FILE = "wi_fi.py"


def start():

    print("Starting Wi-Fi setup...")

    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    ap.active(True)

    ap.config(
        essid=SETUP_SSID,
        password=SETUP_PASSWORD
    )

    ap.ifconfig((
        "192.168.1.1",
        "255.255.255.0",
        "192.168.1.1",
        "192.168.1.1"
    ))

    print("Setup Wi-Fi started")
    print("SSID:", SETUP_SSID)
    print("IP:", ap.ifconfig()[0])

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 80))
    server.listen(1)

    print("Open http://192.168.1.1")

    while True:

        client, addr = server.accept()

        try:
            print("Client:", addr)

            request = client.recv(4096).decode()

            print("Request received")

            # POST - save settings
            if request.startswith("POST"):

                parts = request.split("\r\n\r\n", 1)

                if len(parts) == 2:

                    body = parts[1]

                    params = parse_form(body)

                    ssid = params.get("ssid", "")
                    password = params.get("password", "")

                    print("New SSID:", ssid)

                    save_wifi(ssid, password)

                    response = """
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width">
</head>

<body>

<h2>Wi-Fi settings saved</h2>

<p>SSID: {}</p>

<p>Saved to wi_fi.py</p>

<p>You can restart the ESP32 now.</p>

</body>
</html>
""".format(html_escape(ssid))

                else:

                    response = "<html><body><h2>Invalid request</h2></body></html>"

            else:

                # GET - show form

                ssid, password = load_wifi()

                response = """
<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>Clock Wi-Fi Setup</title>

</head>

<body>

<h2>Clock Wi-Fi Setup</h2>

<form method="POST">

<p>
SSID:<br>
<input
    name="ssid"
    value="{0}"
    style="width:250px">
</p>

<p>
Password:<br>

<input
    id="password"
    type="password"
    name="password"
    value="{1}"
    style="width:250px">

<br>

<label>
<input
    type="checkbox"
    onclick="showPassword()">

Show password
</label>

</p>

<p>

<button type="submit">
Save
</button>

</p>

</form>


<script>

function showPassword()
{{
    var p = document.getElementById("password");

    if (p.type === "password")
    {{
        p.type = "text";
    }}
    else
    {{
        p.type = "password";
    }}
}}

</script>

</body>

</html>
""".format(
                    html_escape(ssid),
                    html_escape(password)
                )

            send_response(client, response)

        except Exception as e:

            print("Setup error:", e)

            try:
                response = """
<html>
<body>
<h2>Setup error</h2>
<p>{}</p>
</body>
</html>
""".format(str(e))

                send_response(client, response)

            except:
                pass

        finally:

            client.close()


def load_wifi():

    try:

        with open(CONFIG_FILE, "r") as f:
            text = f.read()

        ssid = extract_value(text, "SSID")
        password = extract_value(text, "PASSWORD")

        return ssid, password

    except Exception as e:

        print("Cannot read Wi-Fi config:", e)

        return "", ""


def save_wifi(ssid, password):

    with open(CONFIG_FILE, "w") as f:

        f.write("import network\n")
        f.write("import time\n")
        f.write("import ntptime\n\n")

        f.write("SSID = '{}'\n".format(
            escape_python(ssid)
        ))

        f.write("PASSWORD = '{}'\n\n".format(
            escape_python(password)
        ))

        f.write("""
wifi = network.WLAN(network.STA_IF)
wifi.active(True)


def connect_wifi(max_attempts=10):

    if wifi.isconnected():
        print('Already connected! IP:', wifi.ifconfig()[0])
        return True

    print('Connecting to Wi-Fi:', SSID)

    wifi.connect(SSID, PASSWORD)

    attempt = 0

    while not wifi.isconnected() and attempt < max_attempts:

        attempt += 1

        print(
            f'Connecting to Wi-Fi... attempt {attempt}'
        )

        time.sleep(2)

    if wifi.isconnected():

        print(
            'Connected! IP:',
            wifi.ifconfig()[0]
        )

        return True

    print('Failed to connect.')

    return False


def sync_time():

    try:

        ntptime.settime()

        print("Time synchronized via NTP")

    except:

        print("Failed to sync time")
""")


    print("Wi-Fi configuration saved")


def extract_value(text, name):

    marker = name + " = '"

    start = text.find(marker)

    if start == -1:
        return ""

    start += len(marker)

    end = text.find("'", start)

    if end == -1:
        return ""

    return text[start:end]


def parse_form(body):

    result = {}

    for item in body.split("&"):

        parts = item.split("=", 1)

        if len(parts) == 2:

            key = url_decode(parts[0])
            value = url_decode(parts[1])

            result[key] = value

    return result


def url_decode(value):

    value = value.replace("+", " ")

    result = ""

    i = 0

    while i < len(value):

        if value[i] == "%" and i + 2 < len(value):

            try:

                result += chr(
                    int(value[i + 1:i + 3], 16)
                )

                i += 3

                continue

            except:
                pass

        result += value[i]

        i += 1

    return result


def html_escape(value):

    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def escape_python(value):

    return (
        value
        .replace("\\", "\\\\")
        .replace("'", "\\'")
    )


def send_response(client, body):

    data = body.encode()

    header = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(len(data))

    client.send(header.encode())
    client.send(data)
import stairs
import time

stairs.start()

# Try WiFi (optional)
try:
    import wi_fi
    if wi_fi.connect_wifi():
        import web
        import _thread
        _thread.start_new_thread(web.start, ())
    else:
        print("WiFi not available. Running offline.")
except Exception as e:
    print("WiFi/Web failed:", e)
    print("Continuing in offline mode.")

# Основной цикл для удержания ESP32 живым
while True:
    time.sleep(1)
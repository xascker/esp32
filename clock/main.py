import uasyncio as asyncio
import mclock
import web
import wi_fi
import setup_wifi

if not wi_fi.connect_wifi():

    # Connection failed - start Wi-Fi setup
    setup_wifi.start()


# Wi-Fi connected
wi_fi.sync_time()

async def main():
    asyncio.create_task(mclock.clock_loop())
    asyncio.create_task(web.server_loop())

    while True:
        await asyncio.sleep(1)
        
asyncio.run(main())
import uasyncio as asyncio
import mclock
import web 

async def main():
    asyncio.create_task(mclock.clock_loop())
    asyncio.create_task(web.server_loop())

    while True:
        await asyncio.sleep(1)
        
asyncio.run(main())
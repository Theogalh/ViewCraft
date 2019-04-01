from init import client
import asyncio


async def dontcrash():
    while not client.is_closed:
        channels = client.get_all_channels()
        await asyncio.sleep(50)

from omdbie import core
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
loop = asyncio.get_event_loop()
client = core.Client()


async def get(title):
    return await client.by_title_or_id(title)


mag = loop.run_until_complete(get("The Magicians"))
print(mag)
print(mag.year, mag.title, mag.runtime)

mag = loop.run_until_complete(get("Harry Potter"))
print(mag)
print(mag.year, mag.title, mag.runtime)
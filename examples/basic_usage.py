from omdbie import core
import asyncio
import time
import logging

logging.basicConfig(level=logging.INFO)
loop = asyncio.get_event_loop()

ah = time.perf_counter()
client = core.Client()
print("Client imports took {}".format(time.perf_counter() - ah))


async def get(title):
    return await client.by_title_or_id(title)


while True:
    name = input(">")
    resp = loop.run_until_complete(get(str(name)))

    if not resp:
        print("Not found.")
        continue

    print("{} ({}) - {}".format(resp.title, resp.year, resp.runtime))
    print(resp.trailer)
    print(type(resp.genre), resp.genre)

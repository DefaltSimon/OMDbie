"""
Connector part for OMDbie
"""

# Determine library installed
import importlib
import logging
import asyncio

try:
    from ujson import loads
except ImportError:
    from json import loads

from .exceptions import HTTPException

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Connector:
    def __init__(self):
        pass

    @staticmethod
    def _build_url(url: str, **fields):
        if not url.endswith("?"):
            url += "?"

        field_list = ["{}={}".format(key, value) for key, value in fields.items()]
        return str(url) + "&".join(field_list)

    @classmethod
    def get_aiohttp(cls, loop=asyncio.get_event_loop()):
        return AioHttpConnector(loop)

    @classmethod
    def get_requests(cls):
        return RequestsConnector()


class RequestsConnector(Connector):
    def __init__(self):
        super().__init__()

        try:
            self.req = importlib.import_module("requests")
        except ImportError:
            log.critical("Could not import requests")
            raise ImportError("module requests not found")

    def request(self, url, *_, **fields) -> dict:
        # Make a valid url with all the provided fields
        formatted_url = self._build_url(url, **fields)

        resp = self.req.get(formatted_url)

        # Notify if something goes wrong
        if resp.status_code != self.req.codes.ok:
            resp.raise_for_status()

        return loads(resp)


class AioHttpConnector(Connector):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__()

        try:
            self.aio = importlib.import_module("aiohttp")
        except ImportError:
            log.critical("Could not import aiohttp")
            raise ImportError("module aiohttp not found")

        self.loop = loop

    async def request(self, url, *_, **fields) -> dict:
        # Use existing session
        async with self.aio.ClientSession() as s:
            # Make a valid url with all the provided fields
            formatted_url = self._build_url(url, **fields)

            # Send GET request
            async with s.get(formatted_url) as resp:
                # Check if everything is ok
                if not (200 <= resp.status < 300):
                    raise HTTPException("Got status code {}".format(resp.status))

                # Use custom lib for json parsing
                text = await resp.text()
                return loads(text)

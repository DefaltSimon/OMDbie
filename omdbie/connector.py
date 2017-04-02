"""
Connector part for OMDbie
"""

# 3rd party
import importlib
import logging
import asyncio

# Lib imports
from .exceptions import HTTPException, DecodeError

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# ujson is blazing fast, but fall back to standard json if not installed
try:
    from ujson import loads
except ImportError:
    log.warning("ujson not installed, falling back to standard json lib")
    from json import loads


class Connector:
    def __init__(self):
        pass

    @staticmethod
    def _build_url(url: str, **fields) -> str:
        if not url.endswith("?"):
            url += "?"

        field_list = ["{}={}".format(key, value) for key, value in fields.items()]
        return str(url) + "&".join(field_list)

    @classmethod
    def get_urllib(cls):
        return UrllibConnector()

    @classmethod
    def get_aiohttp(cls, loop=asyncio.get_event_loop()):
        return AioHttpConnector(loop)

    @classmethod
    def get_requests(cls):
        return RequestsConnector()


class UrllibConnector(Connector):
    def __init__(self):
        super().__init__()

        # Included in the standard library
        self.urllib = importlib.import_module("urllib")

    def request(self, url, *_, **fields) -> dict:
        # Make a valid url with all the provided fields
        formatted_url = self._build_url(url, **fields)
        log.debug("Requesting json from {}".format(formatted_url))

        with self.urllib.urlopen(formatted_url) as data:
            data = data.read()

        assert data is not None

        try:
            json = loads(data)
        except Exception:
            log.debug("Malformed data: {}".format(data))
            raise DecodeError("malformed json data")

        return json


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
        log.debug("Requesting json from {}".format(formatted_url))

        resp = self.req.get(formatted_url)

        # Notify if something goes wrong
        if resp.status_code != self.req.codes.ok:
            resp.raise_for_status()

        if not resp.text:
            raise DecodeError("empty response")

        return loads(resp.text)


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
            log.debug("Requesting json from {}".format(formatted_url))

            # Send GET request
            async with s.get(formatted_url) as resp:
                # Check if everything is ok
                if not (200 <= resp.status < 300):
                    raise HTTPException("Got status code {}".format(resp.status))

                # Use custom lib for json parsing
                text = await resp.text()

                if not text:
                    raise DecodeError("empty response")

                return loads(text)

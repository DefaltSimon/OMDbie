"""
OMDbie - A python wrapper around http://www.omdbapi.com/
"""

import asyncio
import logging
import time
from typing import Union

from .utils import dict_get_by_value
from ._types import VideoType, PlotLength, Connectors, Endpoints, Movie, Series
from .connector import Connector

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Constants
MAX_CACHE_AGE = 21600


class CacheManager:
    def __init__(self):
        """
        Cache manager for OMDbie
        """
        # Structure:
        # items => imdb_id : data
        # ages  => imdb_id : timestamp (int)
        # timestamps use time.time()

        self.items = {}
        self.ages = {}
        self.titles = {}

    def check_item(self, title_or_imdb_id: str, max_age: int = MAX_CACHE_AGE) -> bool:
        """
        Item search
        :param title_or_imdb_id: imdbID of film/series OR title (must be exact)
        :param max_age: 
        :return: bool - True if item exists AND is not too old
        """
        # If parameter is an imdb id, simply use self.ages, otherwise search through self.titles too
        if title_or_imdb_id.startswith("tt"):
            item_age = self.ages.get(title_or_imdb_id)

        else:
            title = self.titles.get(title_or_imdb_id)

            if title:
                item_age = self.ages.get(title)
            else:
                return False

        # Check if item even exists
        if not item_age:
            return False

        return bool((time.time() - item_age) < max_age)

    def set_item(self, imdb_id: str, data: Union[Series, Movie]):
        """
        Caches an item
        :param imdb_id: imdbID od the entry
        :param data: the corresponding data
        :return: None
        """
        timestamp = time.time()

        self.ages[imdb_id] = timestamp
        self.items[imdb_id] = data
        self.titles[data.title] = imdb_id

        print(self.ages, self.items, self.titles, sep="\n")

    def get_item(self, imdb_id) -> Union[dict, None]:
        """
        Gets an item. This does not check for age (use check_item).
        :param imdb_id: imdbID of entry
        :return: dict, None
        """
        return self.items.get(imdb_id)

    def get_id(self, title) -> Union[str, None]:
        """
        Tries to get title's associated imdbID
        :param title: title of film/series
        :return: str, None
        """
        return self.titles.get(title)


class Client:
    """
    The base Client for OMDbie
    A client must always be created before getting info.
    DO NOT create an instance every time when getting info, as it has dynamic imports!
    """
    def __init__(self, connector: Connectors = "aiohttp", loop=asyncio.get_event_loop()):
        self.loop = loop
        self.cache = CacheManager()

        if connector == Connectors.aiohttp:
            self.http = Connector.get_aiohttp(loop)
        elif connector == Connectors.requests:
            self.http = Connector.get_requests()
        else:
            log.warning("No connector specified, falling back to aiohttp")
            self.http = Connector.get_aiohttp(loop)

    async def by_title_or_id(self, title: str, type_: VideoType = None, year: int = None,  plot: PlotLength = None,
                             read_cache: bool = True, write_cache: bool = True) -> Union[Movie, Series, None]:
        """
        A basic title/IMDb id search on OMDb
        :param title: str
        :param type_: should be one of VideoType
        :param year: int
        :param plot: one of PlotLength
        :param read_cache: bool indicating if you want to even check cache
        :param write_cache: bool indicating if you want to write to cache after fetching
        :return: 
        """
        # Try to get item from cache
        if read_cache and self.cache.check_item(title):
            return self.cache.get_item(self.cache.get_id(title))

        if type_:
            type_ = dict_get_by_value(VideoType.__dict__, type_)
        if plot:
            plot = dict_get_by_value(PlotLength.__dict__, plot)

        fields = {}

        # Handle differently if title is an IMDb id
        if title.startswith("tt"):
            fields["i"] = title
        else:
            fields["t"] = title

        if type_:
            fields["type"] = type_
        if plot:
            fields["plot"] = plot
        if year:
            fields["year"] = int(year)

        data = await self.http.request(Endpoints.base, **fields)

        if data.get("Response") == "False":
            log.debug("Failed: {}".format(data.get("Error")))
            return None

        # Adds additional info
        # 1. Trailer link
        data["trailer"] = "http://www.imdb.com/title/{}/videogallery".format(data.get("imdbID"))

        # Instantiates the objects and saves to cache
        if data.get("Type") == VideoType.series:
            entry = Series(**data)
            if write_cache:
                self.cache.set_item(entry.imdb_id, entry)

            return entry

        elif data.get("Type") == VideoType.movie:
            entry = Movie(**data)
            if write_cache:
                self.cache.set_item(entry.imdb_id, entry)

            return entry

        else:
            log.warning("Data type not recognized: {}".format(data.get("Type")))

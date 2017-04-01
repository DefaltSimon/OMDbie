"""
OMDbie - A python wrapper around http://www.omdbapi.com/
"""

import asyncio
import logging

from .utils import dict_get_by_value
from ._types import VideoType, PlotLength, Connectors, Endpoints, Movie, Series
from .connector import Connector

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Client:
    def __init__(self, connector: Connector = Connectors.aiohttp, loop=asyncio.get_event_loop()) -> (Movie, Series):
        self.loop = loop

        if connector == Connectors.aiohttp:
            self.http = Connector.get_aiohttp(loop)
        elif connector == Connectors.requests:
            self.http = Connector.get_requests()
        else:
            log.warning("No connector specified, falling back to aiohttp")
            self.http = Connector.get_aiohttp(loop)

    async def by_title_or_id(self, title: str, type_: VideoType = None, year: int = None, plot: PlotLength = None):
        """
        A basic title/IMDb id search on OMDb
        :param title: str
        :param type_: should be one of VideoType
        :param year: int
        :param plot: one of PlotLength
        :return: 
        """

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

        if data.get("Response") is "False":
            log.warning("Failed with error: ".format(data.get("Error")))
            return

        if data.get("Type") == VideoType.series:
            return Series(**data)
        elif data.get("Type") == VideoType.movie:
            return Movie(**data)

        else:
            log.warning("Data type not recognized: {}".format(data.get("Type")))

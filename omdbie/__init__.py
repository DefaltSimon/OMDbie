"""

OMDbie - A python 3 library for fetching info about films.
Uses http://www.omdbapi.com/

"""

from .core import Client
from ._types import Series, Movie, VideoType, PlotLength, Connectors
from .connector import Connector
from .exceptions import HTTPException

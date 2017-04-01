"""
Types for OMDbie
"""


class VideoType:
    movie = "movie"
    series = "series"
    episode = "episode"


class PlotLength:
    short = "short"
    full = "full"


class Connectors:
    requests = "requests"
    aiohttp = "aiohttp"


class Endpoints:
    base = "http://www.omdbapi.com/?"


movie_transcodes = {
    "BoxOffice": "box_office",
    "imdbRating": "imdb_rating",
    "imdbVotes": "imdb_votes",
    "imdbID": "imdb_id"
}


class Movie:
    __slots__ = (
        "title", "year", "rated", "released", "runtime", "genre", "director", "writer",
        "actors", "plot", "language", "country", "poster", "ratings", "metascore",
        "imdb_rating", "imdb_votes", "imdb_id", "type", "dvd", "box_office", "production",
        "website", "awards", "total_seasons"
    )

    def __init__(self, **fields):
        # Shift specified keys to camel_case instead of camelCase
        for key_from, key_to in movie_transcodes.items():
            if fields.get(key_from):
                fields[key_to] = fields.get(key_from)
                del fields[key_from]

        for name, value in fields.items():
            try:
                self.__setattr__(name.lower(), value)
            except AttributeError:
                pass


series_transcodes = {
    "totalSeasons": "total_seasons",
}


class Series(Movie):
    # Keeps Movie's __slots__
    __slots__ = ()

    def __init__(self, **fields):
        super().__init__(**fields)

        for key_from, key_to in series_transcodes.items():
            if fields.get(key_from):
                fields[key_to] = fields.get(key_from)
                del fields[key_from]

        for name, value in fields.items():
            try:
                self.__setattr__(name.lower(), value)
            except AttributeError:
                pass

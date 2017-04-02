"""
Exceptions for OMDbie
"""


class HTTPException(Exception):
    """
    Used when a Requestor encounters an error
    """
    pass


class DecodeError(Exception):
    """
    Used when invalid response is gotten
    """
    pass

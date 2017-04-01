"""
Different utilities for OMDbie
"""


def dict_get_by_value(dict_: dict, value):
    for k, v in dict_.items():
        if v == value:
            return k

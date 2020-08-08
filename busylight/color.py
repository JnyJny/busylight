"""turn strings into RGB
"""

from functools import lru_cache
from math import log
from string import hexdigits
from typing import Tuple

import webcolors


def normalize_hex_str(value: str) -> str:
    """Given a `value`, normalizes hex strings to webcolor format.

    The function checks for known hexadecimal string prefixes; 0x
    and # and normalizes the string to the # notation used by
    webcolors. Also checks for a bare hexadecimal value, checking
    that all characters are valid hex digits. 

    :param str: possible hexadecimal string
    :return: normalized hexadecimal string 

    Raises:
    - ValueError Unrecognized hex string

    """

    try:
        if value[0] == "#":
            return value.lower()

        if value[0:2] in ["0x", "0X"]:
            return "#" + value[2:].lower()

        if all(c in hexdigits for c in value):
            return "#" + value.lower()
    except (TypeError, IndexError, KeyError):
        pass

    raise ValueError(f"Unrecognized hex string '{value}'")


def color_to_rgb(value: str) -> Tuple[int, int, int]:
    """Returns a tuple of red, green and blue integer values.

    The input string string can be a hexadecimal string that
    optionally starts with 0x or # or a color name.
    
    Examples of 'red':
    - 0xf00
    - #f00
    - f00
    - 0xff0000
    - #ff0000
    - ff0000
    - red

    Raises:
    - ValueError Unable to decode color string
    """

    try:
        return tuple(webcolors.hex_to_rgb(normalize_hex_str(value)))
    except ValueError:
        pass

    return tuple(webcolors.name_to_rgb(value))


@lru_cache(maxsize=255)
def gamma_correct(value: int, step: int = 255) -> int:
    """
    """
    return round((log(1 + value) / 5.545) * step)

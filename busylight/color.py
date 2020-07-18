"""
"""

from functools import lru_cache
from math import log
from typing import Tuple

import webcolors


def color_to_rgb(value: str) -> Tuple[int, int, int]:
    """Returns a tuple of red, green and blue integer values
    interpreted from the input string. The string can be a
    hexadecimal string that starts with 0x or # or a color name.

    Raises:
    - ValueError
    """

    if value.startswith("0x"):
        return tuple(webcolors.hex_to_rgb("#" + value[2:]))

    if value.startswith("#"):
        return tuple(webcolors.hex_to_rgb(value))

    return tuple(webcolors.name_to_rgb(value))


@lru_cache(maxsize=255)
def gamma_correct(value: int, step: int = 255) -> int:
    return round((log(1 + value) / 5.545) * step)

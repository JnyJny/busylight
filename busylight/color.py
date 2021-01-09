"""turn strings into RGB
"""

from functools import lru_cache
from math import log
from string import hexdigits
from typing import Iterable, Tuple

import webcolors

ColorTuple = Tuple[int, int, int]


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
        r, g, b = webcolors.hex_to_rgb(normalize_hex_str(value))
        return (int(r), int(g), int(b))
    except ValueError:
        pass

    r, g, b = webcolors.name_to_rgb(value)
    return (int(r), int(g), int(b))


def rgb_to_hex(red: int, green: int, blue: int, prefix: str = "#") -> str:
    """"""
    return f"{prefix}{red:02x}{green:02x}{blue:02x}"


class ColorCorrect:
    def __init__(
        self,
        gamma: Tuple[float, float, float] = None,
        white: Tuple[int, int, int] = None,
    ) -> None:
        self.gamma = gamma or (2.0, 2.0, 2.0)
        self.white = white or (255, 255, 255)

    @lru_cache(maxsize=256)
    def correct_value(self, value: int, gamma: float, white: int) -> int:
        """
        :param value: int
        :param gamma: float
        :param white: int
        """
        return int(white * (value / 255) ** gamma)

    def correct(
        self, color: Tuple[int, int, int], gamma: Tuple[float, float, float] = None
    ) -> Tuple[int, int, int]:
        """
        :param color: Tuple[int, int, int]
        :param gamma: Tuple[float, float, float] optional
        :return: Tuple[int, int, int]
        """
        gamma = gamma or self.gamma
        corrected = []
        for v, g, w in zip(color, gamma, self.white):
            corrected.append(self.correct_value(v, g, w))
        r, g, b = corrected
        return (r, g, b)


@lru_cache(maxsize=255)
def gamma_correct(value: int, step: int = 255) -> int:
    """"""
    gamma = 5.545
    return round((log(1 + value) / gamma) * step)

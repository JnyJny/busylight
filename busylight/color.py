"""
"""

from typing import List, Tuple

import webcolors

from loguru import logger

ColorTuple = Tuple[int, int, int]
ColorList = List[ColorTuple]


class ColorLookupError(Exception):
    pass


def parse_color_string(value: str, scale: float = 1.0) -> ColorTuple:
    """Convert a string to a 24-bit three channel (RGB) color.

    String values can be:
    - a webcolors recognized color name
    - a 24 or 12-bit hex string prefaced with `#`
    - a 24 or 12-bit hex string prefaced with `0x`
    - a bare 24 or 12-bit hex string

    Optionally scales color intensities of all three channels if
    `scale` is less than 1.0 and greater than or equal to zero.

    If scale is zero, the resulting color is always black.
    If scale is one, the color is unchanged.

    :param value: str
    :param scale: float range [0.0, 1.0]

    Raises:
    - ColorLookupError
    """

    scale = max(0.0, min(scale, 1.0))

    try:
        return scale_color(tuple(webcolors.name_to_rgb(value)), scale)
    except ValueError as error:
        logger.info(f"name_to_rgb {value} -> {error}")

    value = value.lower().replace("0x", "#")

    if not value.startswith("#"):
        value = "#" + value

    try:
        return scale_color(tuple(webcolors.hex_to_rgb(value)), scale)

    except ValueError as error:
        logger.error(f"{value} -> {error}")

    raise ColorLookupError(f"No color mapping for {value}")


def colortuple_to_name(color: ColorTuple) -> str:
    """Returns a string name of the given ColorTuple if found.

    :color: ColorTuple
    :return: str

    Raises:
    - ColorLookupError
    """
    try:
        return webcolors.rgb_to_name(color)
    except ValueError as error:
        logger.error(f"{color} -> {error}")

    raise ColorLookupError(f"No color mapping for {color}")


def scale_color(color: ColorTuple, scale: float = 1.0) -> ColorTuple:
    """Returns a ColorTuple whose color intensity scaled by the given value.

    Each of the component values of the ColorTuple are multiplied by scale
    which is assumed to range from 0.0 to 1.0 corresponding to 0% to 100%
    intensitity.

    :param color: ColorTuple
    :param scale: float
    :return: ColorTuple
    """

    return tuple(max(0, min(255, round(v * scale))) for v in color)

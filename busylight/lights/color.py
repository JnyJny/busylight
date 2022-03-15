"""
"""

from typing import List, Tuple

import webcolors

from loguru import logger

ColorTuple = Tuple[int, int, int]
ColorList = List[ColorTuple]


def parse_color(value: str) -> ColorTuple:
    """Convert a string to a 24-bit color, 3 channel color.

    String values can be:
    - a webcolors recognized color name
    - a 24 or 12-bit hex string prefaced with `#`
    - a 24 or 12-bit hex string prefaced with `0x`
    - a bare 24 or 12-bit hex string
    """

    try:
        return tuple(webcolors.name_to_rgb(value))
    except ValueError as error:
        logger.debug(f"name_to_rgb {value=} {error}")

    value = value.lower().replace("0x", "#")
    if not value.startswith("#"):
        value = "#" + value
    try:
        return tuple(webcolors.hex_to_rgb(value))
    except ValueError as error:
        logger.debug(f"hex_to_rgb {value} -> {error}")
        raise ValueError(f"No color mapping for {value}") from None

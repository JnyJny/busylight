""" """

import webcolors
from loguru import logger


class ColorLookupError(Exception):
    pass


def parse_color_string(value: str, scale: float = 1.0) -> tuple[int, int, int]:
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

    if value.startswith("0x") or value.startswith("0X"):
        value = f"#{value[2:]}"

    if value.startswith("#"):
        try:
            rgb = webcolors.hex_to_rgb(value)
            return scale_color(rgb, scale)
        except ValueError as error:
            logger.debug(f"No match found for {value} -> {error}")
            raise ColorLookupError(f"No color mapping for {value}") from error

    for spec in [
        webcolors.CSS3,
        webcolors.CSS2,
        webcolors.CSS21,
        webcolors.HTML4,
    ]:
        try:
            rgb = webcolors.name_to_rgb(value, spec=spec)
            return scale_color(rgb, scale)
        except ValueError as error:
            logger.info(f"name_to_rgb[{spec}] {value} ->  {error}")

    raise ColorLookupError(f"No color mapping for {value}")


def colortuple_to_name(color: tuple[int, int, int]) -> str:
    """Return a string name of the given tuple[int, int, int].

    A RGB tuple is returned if found otherwise returns a normalized
    string represetnation of a 24-bit hexadecimal number prefaced with
    an octothorpe.

    :param color: tuple[int, int, int]

    """
    try:
        return webcolors.rgb_to_name(color)
    except ValueError:
        logger.debug(f"No match found for {color}")

    return webcolors.rgb_to_hex(color)


def scale_color(
    color: tuple[int, int, int],
    scale: float = 1.0,
) -> tuple[int, int, int]:
    """Returns a tuple[int, int, int] whose color intensity scaled by the given value.

    Each of the component values of the tuple[int, int, int] are multiplied by scale
    which is assumed to range from 0.0 to 1.0 corresponding to 0% to 100%
    intensitity.

    :param color: tuple[int, int, int]
    """

    if scale == 1.0:
        return color

    if scale == 0.0:
        return (0, 0, 0)

    r, g, b = [max(0, min(255, round(v * scale))) for v in color]

    return (r, g, b)

"""Shared color definitions for early Blynclight devices (VID 0x1130).

Both the BLYNCUSB10 and BLYNCUSB20 support the same 7 predefined colors
plus OFF. This module provides the color enum, RGB mappings, and a
nearest-color matching function for the busylight-core RGB interface.
"""

from enum import IntEnum


class BlyncusbColor(IntEnum):
    """Predefined color values for early Blynclight devices.

    The blynux protocol uses a 4-bit color mask in the high nibble
    of byte 7. These values are the mask before shifting.
    """

    WHITE = 0x8
    CYAN = 0x9
    MAGENTA = 0xA
    BLUE = 0xB
    YELLOW = 0xC
    GREEN = 0xD
    RED = 0xE
    OFF = 0xF


BLYNCUSB_COLOR_TO_RGB: dict[BlyncusbColor, tuple[int, int, int]] = {
    BlyncusbColor.WHITE: (255, 255, 255),
    BlyncusbColor.CYAN: (0, 255, 255),
    BlyncusbColor.MAGENTA: (255, 0, 255),
    BlyncusbColor.BLUE: (0, 0, 255),
    BlyncusbColor.YELLOW: (255, 255, 0),
    BlyncusbColor.GREEN: (0, 255, 0),
    BlyncusbColor.RED: (255, 0, 0),
    BlyncusbColor.OFF: (0, 0, 0),
}


RGB_TO_BLYNCUSB_COLOR: dict[tuple[int, int, int], BlyncusbColor] = {
    rgb: color for color, rgb in BLYNCUSB_COLOR_TO_RGB.items()
}


def snap_color(red: int, green: int, blue: int) -> tuple[int, int, int]:
    """Map an RGB color to the nearest predefined Blyncusb palette color.

    Since these devices only support 7 colors plus OFF, this finds
    the best match based on which channels are dominant and returns
    the canonical RGB for that palette entry.

    :param red: Red component (0-255)
    :param green: Green component (0-255)
    :param blue: Blue component (0-255)
    :return: The canonical RGB tuple for the nearest palette color
    """
    if red < 32 and green < 32 and blue < 32:
        return (0, 0, 0)

    max_val = max(red, green, blue)
    threshold = max_val * 0.5

    r_on = red >= threshold
    g_on = green >= threshold
    b_on = blue >= threshold

    color_map: dict[tuple[bool, bool, bool], tuple[int, int, int]] = {
        (True, True, True): (255, 255, 255),
        (True, True, False): (255, 255, 0),
        (True, False, True): (255, 0, 255),
        (False, True, True): (0, 255, 255),
        (True, False, False): (255, 0, 0),
        (False, True, False): (0, 255, 0),
        (False, False, True): (0, 0, 255),
    }

    return color_map.get((r_on, g_on, b_on), (0, 0, 0))


def rgb_to_blyncusb_color(red: int, green: int, blue: int) -> BlyncusbColor:
    """Map an RGB color to the nearest predefined BlyncusbColor enum.

    Convenience wrapper around snap_color for protocol code that
    needs the enum value directly.

    :param red: Red component (0-255)
    :param green: Green component (0-255)
    :param blue: Blue component (0-255)
    :return: The closest BlyncusbColor match
    """
    return RGB_TO_BLYNCUSB_COLOR.get(snap_color(red, green, blue), BlyncusbColor.OFF)

"""TENX20 chipset color codes for BLYNCUSB20 devices.

The TENX20 chipset uses single-byte color codes that differ from
the blynux color mask values used by BLYNCUSB10 devices.
"""

from enum import IntEnum

from .blyncusb_colors import BlyncusbColor


class Tenx20Color(IntEnum):
    """Color codes for TENX20 chipset (PID 0x1E00).

    Single-byte color codes used in the TENX20 protocol.
    """

    RED = 0x60
    GREEN = 0xD8
    BLUE = 0x35
    YELLOW = 0x40
    MAGENTA = 0x20
    WHITE = 0x07
    CYAN = 0x17
    OFF = 0x73


BLYNCUSB_TO_TENX20: dict[BlyncusbColor, Tenx20Color] = {
    BlyncusbColor.RED: Tenx20Color.RED,
    BlyncusbColor.GREEN: Tenx20Color.GREEN,
    BlyncusbColor.BLUE: Tenx20Color.BLUE,
    BlyncusbColor.YELLOW: Tenx20Color.YELLOW,
    BlyncusbColor.MAGENTA: Tenx20Color.MAGENTA,
    BlyncusbColor.WHITE: Tenx20Color.WHITE,
    BlyncusbColor.CYAN: Tenx20Color.CYAN,
    BlyncusbColor.OFF: Tenx20Color.OFF,
}

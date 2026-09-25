"""VT DND enumerations.

This module defines the enumerations used by VT DND devices for
HID reports, command actions, brightness levels, and flash modes.
"""

from enum import IntEnum


class Report(IntEnum):
    """HID report numbers used for communication with VT devices."""

    ONE = 1


class Action(IntEnum):
    """Commands understood by VT DND devices."""

    Off = 0x01
    Flash = 0x02
    SetColor = 0x04
    SetBrightness = 0x09


class Brightness(IntEnum):
    """Brightness levels supported by VT DND devices."""

    Low = 1
    Medium = 2
    High = 3


class FlashMode(IntEnum):
    """Flash patterns predefined in VT DND firmware."""

    ONE = 1
    TWO = 2

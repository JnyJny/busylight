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


class DNDFlashMode(IntEnum):
    """Breathing patterns built into VT DND firmware.

    Each pattern fades a fixed color in and out; the light's current
    color is ignored.
    """

    Red = 1
    Blue = 2

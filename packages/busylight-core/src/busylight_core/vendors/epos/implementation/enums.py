"""EPOS Busylight enumerations.

This module defines the enumerations used by EPOS Busylight devices for
actions and report types.
"""

from enum import IntEnum


class Action(IntEnum):
    """Action enumeration for EPOS Busylight device commands.

    Defines the available actions that can be performed on EPOS devices.
    The SetColor action controls the LED color and state.
    """

    SetColor = 0x1202


class Report(IntEnum):
    """Report type enumeration for HID communication.

    Defines the HID report numbers used for communication with EPOS devices.
    """

    ONE = 1

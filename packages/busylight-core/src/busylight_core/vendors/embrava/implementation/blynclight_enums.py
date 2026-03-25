"""Embrava Blynclight enumerations.

This module defines the enumerations used by Embrava Blynclight devices
for flash speed control and other device behaviors.
"""

from enum import IntEnum


class BlynclightFlashSpeed(IntEnum):
    """Flash speed enumeration for Embrava Blynclight devices.

    Defines the available flash speeds for the LED indicator.
    These values control how quickly the device cycles when in flash mode.
    """

    slow = 1
    medium = 2
    fast = 4

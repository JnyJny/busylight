"""Luxafor Flag enumerations.

This module defines the enumerations used by Luxafor Flag devices for
commands, LED selection, patterns, and wave effects.
"""

from enum import IntEnum


class Command(IntEnum):
    """Command enumeration for Luxafor Flag device operations.

    Defines the available commands that can be sent to Luxafor devices
    to control colors, effects, and patterns.
    """

    Color = 1
    Fade = 2
    Strobe = 3
    Wave = 4
    Pattern = 6


class LEDS(IntEnum):
    """LED selection enumeration for Luxafor Flag devices.

    Defines which LEDs to target with commands. Luxafor (Flag) devices
    have six individual LEDs that can be controlled independently or as
    groups.
    """

    All = 0xFF
    Back = 0x41
    Front = 0x42
    LED1 = 0x1
    LED2 = 0x2
    LED3 = 0x3
    LED4 = 0x4
    LED5 = 0x5
    LED6 = 0x6


class Pattern(IntEnum):
    """Pattern enumeration for built-in Luxafor effects.

    Defines the available pre-programmed patterns that can be
    displayed on Luxafor devices without custom programming.
    """

    Off = 0
    TrafficLight = 1
    Random1 = 2
    Random2 = 3
    Random3 = 4
    Police = 5
    Random4 = 6
    Random5 = 7
    Rainbow = 8


class Wave(IntEnum):
    """Wave effect enumeration for Luxafor devices.

    Defines the available wave patterns that create flowing
    color effects across the LED array.
    """

    Off = 0
    Short = 1
    Long = 2
    ShortOverLapping = 3
    LongOverlapping = 4
    WAVE5 = 5

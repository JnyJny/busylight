"""
"""

from enum import IntEnum


class Command(IntEnum):
    Color = 1
    Fade = 2
    Strobe = 3
    Wave = 4
    Pattern = 6


class LEDS(IntEnum):
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
    Off = 0
    Short = 1
    Long = 2
    ShortOverLapping = 3
    LongOverlapping = 4
    WAVE5 = 5

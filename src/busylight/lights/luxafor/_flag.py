""" """

from enum import IntEnum, auto


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
    Off = auto()
    TrafficLight = auto()
    Random1 = auto()
    Random2 = auto()
    Random3 = auto()
    Police = auto()
    Random4 = auto()
    Random5 = auto()
    Rainbow = auto()


class Wave(IntEnum):
    Off = auto()
    Short = auto()
    Long = auto()
    ShortOverLapping = auto()
    LongOverlapping = auto()
    WAVE5 = auto()

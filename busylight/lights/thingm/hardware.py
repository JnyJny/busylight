"""
"""

from enum import Enum
from typing import Tuple

from ..statevector import StateField, StateVector


class Blink1Action(int, Enum):
    FadeColor = ord("c")
    SetColor = ord("n")
    ReadColor = ord("r")
    ServerTickle = ord("D")
    PlayLoop = ord("p")
    PlayStateRead = ord("S")
    SetColorPattern = ord("P")
    SaveColorPatterns = ord("W")
    ReadColorPattern = ord("R")
    SetLEDn = ord("l")
    ReadEEPROM = ord("e")
    WriteEEPROM = ord("E")
    GetVersion = ord("v")
    TestCommand = ord("!")
    WriteNote = ord("F")
    ReadNote = ord("f")
    Bootloader = ord("G")
    LockBootLoader = ord("L")
    SetStartupParams = ord("B")
    GetStartupParams = ord("b")
    ServerModeTickle = ord("D")
    GetChipID = ord("U")


class Blink1LED(int, Enum):
    ALL = 0
    TOP = 1
    BOTTOM = 2


class Blink1Report(int, Enum):
    ONE = 1
    TWO = 2


class Blink1ReportField(StateField):
    """An 8-bit report field."""


class Blink1ActionField(StateField):
    """An 8-bit action."""


class Blink1ColorField(StateField):
    """An 8-bit color value."""


class Blink1PlayField(StateField):
    """An 8-bit value."""


class Blink1StartField(StateField):
    """An 8-bit value."""


class Blink1StopField(StateField):
    """An 8-bit value."""


class Blink1CountField(StateField):
    """An 8-bit count value."""


class Blink1FadeField(StateField):
    """An 8-bit fade duty cycle value."""


class Blink1LEDSField(StateField):
    """An 8-bit field."""


class Blink1LineField(StateField):
    """An 8-bit field."""


class Blink1State(StateVector):
    """"""

    def __init__(self):
        super().__init__(Blink1Report.ONE << 56, 64)

    report = Blink1ReportField(56, 8)
    action = Blink1ActionField(48, 8)

    red = Blink1ColorField(40, 8)
    play = Blink1PlayField(40, 8)

    green = Blink1ColorField(32, 8)
    start = Blink1StartField(32, 8)

    blue = Blink1ColorField(24, 8)
    stop = Blink1StopField(24, 8)

    count = Blink1CountField(16, 8)
    fade = Blink1FadeField(8, 16)

    leds = Blink1LEDSField(0, 8)
    line = Blink1LineField(0, 8)

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self.red, self.green, self.blue = values

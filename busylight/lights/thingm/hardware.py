"""ThingM Hardware Details
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


class ReportField(StateField):
    """An 8-bit report field."""


class ActionField(StateField):
    """An 8-bit action."""


class ColorField(StateField):
    """An 8-bit color value."""


class PlayField(StateField):
    """An 8-bit value."""


class StartField(StateField):
    """An 8-bit value."""


class StopField(StateField):
    """An 8-bit value."""


class CountField(StateField):
    """An 8-bit count value."""


class FadeField(StateField):
    """An 16-bit fade duty cycle value."""


class LEDField(StateField):
    """An 8-bit field."""


class PatternIndexField(StateField):
    """An 8-bit field."""


class BlinkCommand(StateVector):
    """"""

    def __init__(self):
        super().__init__(0, 64)

    report = ReportField(56, 8)
    action = ActionField(48, 8)

    arg0 = StateField(40, 8)
    arg1 = StateField(32, 8)
    arg2 = StateField(24, 8)
    arg3 = StateField(16, 8)
    arg4 = StateField(8, 8)
    arg5 = StateField(0, 8)

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.arg0, self.arg1, self.arg2)

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self.arg0, self.arg1, self.arg2 = values  # type: ignore


class BlinkColorCommand(BlinkCommand):
    @classmethod
    def fade_to_color(
        cls, color: Tuple[int, int, int], fade_ms: int, leds: Blink1LED = Blink1LED.ALL
    ):
        return cls(Blink1Action.FadeColor, color, fade_ms, leds)

    @classmethod
    def set_color(cls, color: Tuple[int, int, int], leds: Blink1LED = Blink1LED.ALL):
        return cls(Blink1Action.SetColor, color, 0, leds)

    @classmethod
    def read_color(cls, leds: Blink1LED = Blink1LED.ALL):
        return cls(Blink1Action.ReadColor, color=(leds.value, 0, 0), leds=leds)

    def __init__(
        self,
        action: int,
        color: Tuple[int, int, int] = None,
        fade_ms: int = 0,
        leds: Blink1LED = Blink1LED.ALL,
    ):
        color = color or (0, 0, 0)
        super().__init__()
        self.report = Blink1Report.ONE.value  # type: ignore
        self.action = action  # type: ignore
        if any(color):
            self.color = color
        self.fade = fade_ms  # type: ignore
        self.leds = leds.value  # type: ignore
        self.default = self.value

    red = ColorField(40, 8)
    green = ColorField(32, 8)
    blue = ColorField(24, 8)
    fade = FadeField(8, 16)
    leds = LEDField(0, 8)


class BlinkPatternCommand(BlinkColorCommand):
    @classmethod
    def set_pattern(cls, color: Tuple[int, int, int], fade_ms: int, index: int):
        return cls(Blink1Action.SetColorPattern, color, fade_ms, index)

    @classmethod
    def save_patterns(cls):
        return cls(Blink1Action.SaveColorPatterns, (0, 0, 0), 0, 0)

    @classmethod
    def read_pattern(cls, index: int):
        return cls(Blink1Action.ReadColorPattern, (0, 0, 0), 0, index)

    def __init__(
        self,
        action: Blink1Action,
        color: Tuple[int, int, int],
        fade_ms: int,
        index: int,
    ):
        super().__init__(
            action,
            color,
            fade_ms,
            leds=index,  # type: ignore
        )

    index = PatternIndexField(0, 8)

"""
"""

from enum import IntEnum
from typing import Tuple

from bitvector import BitField, BitVector


class Action(IntEnum):
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


class LEDS(IntEnum):
    All = 0
    Top = 1
    Bottom = 2


class Report(IntEnum):
    One = 1
    Two = 2


class ReportField(BitField):
    """An 8-bit report field."""


class ActionField(BitField):
    """An 8-bit action."""


class ColorField(BitField):
    """An 8-bit color value."""


class PlayField(BitField):
    """An 8-bit value."""


class StartField(BitField):
    """An 8-bit value."""


class StopField(BitField):
    """An 8-bit value."""


class CountField(BitField):
    """An 8-bit count value."""


class FadeField(BitField):
    """An 16-bit fade duty cycle value."""


class LEDField(BitField):
    """An 8-bit field."""


class PatternIndexField(BitField):
    """An 8-bit field."""


class Command(BitVector):
    """"""

    def __init__(self):
        super().__init__(0, 64)
        self.default = 0

    report = ReportField(56, 8)
    action = ActionField(48, 8)

    red = ColorField(40, 8)
    play = BitField(40, 8)

    green = ColorField(32, 8)
    start = BitField(32, 8)

    blue = ColorField(24, 8)
    stop = BitField(24, 8)

    count = BitField(16, 8)

    fade = FadeField(8, 16)

    leds = LEDField(0, 8)
    line = BitField(0, 8)

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, color: Tuple[int, int, int]) -> None:
        self.red, self.green, self.blue = color  # type: ignore

    def reset(self) -> None:
        """Reset command state to default value."""
        self.value = self.default

    def fade_to_color(
        self,
        color: Tuple[int, int, int],
        fade_ms: int = 10,
        leds: LEDS = LEDS.All,
    ) -> None:
        """ """
        self.reset()
        self.report = Report.One
        self.action = Action.FadeColor
        self.color = color
        self.fade = fade_ms
        self.leds = leds

    def write_pattern_line(
        self,
        color: Tuple[int, int, int],
        fade_ms: int,
        index: int,
    ) -> None:
        """ """
        self.reset()
        self.report = Report.One
        self.action = Action.SetColorPattern
        self.color = color
        self.fade = fade_ms
        self.line = index

    def save_patterns(self) -> None:
        """ """
        self.reset()
        self.report = Report.One
        self.action = Action.SaveColorPatterns
        self.color = (0xBE, 0xEF, 0xCA)
        self.count = 0xFE

    def play_loop(self, play: int, start: int, stop: int, count: int = 0) -> None:
        """ """
        self.reset()
        self.report = Report.One
        self.action = Action.PlayLoop
        self.play = play
        self.start = start
        self.stop = stop
        self.count = count

    def clear_patterns(self, start: int = 0, count: int = 16) -> None:
        """ """
        for index in range(start, start + count):
            self.write_pattern_line((0, 0, 0), 0, index)

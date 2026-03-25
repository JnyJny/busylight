"""ThingM Blink(1) device state management.

This module defines the State class that manages command construction
and device control for ThingM Blink(1) devices, including color control,
pattern management, and LED selection.
"""

from busylight_core.word import Word

from .enums import LEDS, Action, Report
from .fields import (
    ActionField,
    BlueField,
    CountField,
    FadeField,
    GreenField,
    LedsField,
    LinesField,
    PlayField,
    RedField,
    ReportField,
    StartField,
    StopField,
)


class State(Word):
    """Complete device state for ThingM Blink(1) commands.

    The State class manages command construction for Blink(1) devices.
    It provides high-level methods for color control, pattern management,
    and device configuration while handling the low-level bit manipulation
    required for device communication.
    """

    def __init__(self) -> None:
        super().__init__(0, 64)
        self.nleds = 2

    report = ReportField()
    action = ActionField()
    red = RedField()
    green = GreenField()
    blue = BlueField()
    play = PlayField()  # alias for red
    start = StartField()  # alias for green
    stop = StopField()  # alias for blue
    count = CountField()
    fade = FadeField()
    leds = LedsField()
    line = LinesField()  # alias for leds

    @property
    def color(self) -> tuple[int, int, int]:
        """Get the current RGB color as a tuple."""
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, values: tuple[int, int, int]) -> None:
        """Set the RGB color from a tuple."""
        self.red, self.green, self.blue = values

    def fade_to_color(
        self,
        color: tuple[int, int, int],
        fade_ms: int = 10,
        leds: LEDS = LEDS.All,
    ) -> None:
        """Configure device to fade to specified color.

        :param color: RGB color tuple (red, green, blue) with values 0-255
        :param fade_ms: Fade duration in milliseconds
        :param leds: Which LEDs to control (All, Top, or Bottom)
        """
        self.clear()
        self.report = Report.One
        self.action = Action.FadeColor
        self.color = color
        self.fade = fade_ms
        self.leds = leds

    def write_pattern_line(
        self,
        color: tuple[int, int, int],
        fade_ms: int,
        index: int,
    ) -> None:
        """Write a single line to the device's pattern memory.

        :param color: RGB color tuple for this pattern line
        :param fade_ms: Fade duration for this pattern step
        :param index: Pattern line index (0-15)
        """
        self.clear()
        self.report = Report.One
        self.action = Action.SetColorPattern
        self.color = color
        self.fade = fade_ms
        self.line = index

    def save_patterns(self) -> None:
        """Save current pattern memory to device flash storage."""
        self.clear()
        self.report = Report.One
        self.action = Action.SaveColorPatterns
        self.color = (0xBE, 0xEF, 0xCA)
        self.count = 0xFE

    def play_loop(self, play: int, start: int, stop: int, count: int = 0) -> None:
        """Start pattern playback loop.

        :param play: Play mode (0=stop, 1=play)
        :param start: Starting pattern line index
        :param stop: Ending pattern line index
        :param count: Number of loops (0=infinite)
        """
        self.clear()
        self.report = Report.One
        self.action = Action.PlayLoop
        self.play = play
        self.start = start
        self.stop = stop
        self.count = count

    def clear_patterns(self, start: int = 0, count: int = 16) -> None:
        """Clear pattern memory by writing black to specified range.

        :param start: Starting pattern line index
        :param count: Number of pattern lines to clear
        """
        for index in range(start, start + count):
            self.write_pattern_line((0, 0, 0), 0, index)

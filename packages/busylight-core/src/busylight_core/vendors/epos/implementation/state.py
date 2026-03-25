"""EPOS Busylight device state management.

This module defines the State class that manages command construction
for EPOS Busylight devices, including dual-LED control and device configuration.
"""

from busylight_core.word import Word

from .fields import ActionField, ColorField, OnField, ReportField


class State(Word):
    """Complete device state for EPOS Busylight commands.

    The State class manages command construction for EPOS devices.
    It supports dual-LED control with independent color settings for
    each LED, allowing for more complex status indication patterns.
    """

    def __init__(self) -> None:
        super().__init__(0, 80)
        self.nleds = 2

    report = ReportField(72, 8)
    action = ActionField(56, 16)

    red0 = ColorField(48, 8)
    green0 = ColorField(40, 8)
    blue0 = ColorField(32, 8)

    red1 = ColorField(24, 8)
    green1 = ColorField(16, 8)
    blue1 = ColorField(8, 8)

    on = OnField(0, 8)

    @property
    def color0(self) -> tuple[int, int, int]:
        """Get the first LED color as a tuple of RGB values."""
        return (self.red0, self.green0, self.blue0)

    @color0.setter
    def color0(self, color: tuple[int, int, int]) -> None:
        """Set the first LED color from RGB tuple."""
        self.red0, self.green0, self.blue0 = color

    @property
    def color1(self) -> tuple[int, int, int]:
        """Get the second LED color as a tuple of RGB values."""
        return (self.red1, self.green1, self.blue1)

    @color1.setter
    def color1(self, color: tuple[int, int, int]) -> None:
        """Set the second LED color from RGB tuple."""
        self.red1, self.green1, self.blue1 = color

    @property
    def color(self) -> tuple[int, int, int]:
        """Get the first non-black LED color as a tuple of RGB values.

        Returns the color of the first LED that has a non-zero color value,
        or black (0,0,0) if both LEDs are off.
        """
        for color in (self.color0, self.color1):
            if any(color):
                return color
        return (0, 0, 0)

    @color.setter
    def color(self, color: tuple[int, int, int]) -> None:
        """Set both LEDs to the same color."""
        self.color0 = color
        self.color1 = color

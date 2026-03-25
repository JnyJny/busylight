"""Agile Innovative BlinkStick device state management.

This module defines the State class that manages command construction
for BlinkStick devices, including LED arrays and color format conversion.
"""

from __future__ import annotations

import contextlib


class State:
    """BlinkStick State manager for multi-LED devices.

    BlinkStick devices store colors in Green-Red-Blue (GRB) format internally,
    while the public API uses the standard Red-Green-Blue (RGB) format.
    This class handles the conversion automatically and supports multiple
    device variants with different LED counts and report formats.
    """

    @classmethod
    def blinkstick(cls) -> State:
        """Create state for original BlinkStick (single LED, report 1)."""
        return cls(report=1, nleds=1)

    @classmethod
    def blinkstick_pro(cls) -> State:
        """Create state for BlinkStick Pro (192 LEDs, report 2)."""
        return cls(report=2, nleds=192)

    @classmethod
    def blinkstick_square(cls) -> State:
        """Create state for BlinkStick Square (8 LEDs, report 6)."""
        return cls(report=6, nleds=8)

    @classmethod
    def blinkstick_strip(cls) -> State:
        """Create state for BlinkStick Strip (8 LEDs, report 6)."""
        return cls(report=6, nleds=8)

    @classmethod
    def blinkstick_nano(cls) -> State:
        """Create state for BlinkStick Nano (2 LEDs, report 6)."""
        return cls(report=6, nleds=2)

    @classmethod
    def blinkstick_flex(cls) -> State:
        """Create state for BlinkStick Flex (32 LEDs, report 6)."""
        return cls(report=6, nleds=32)

    def __init__(self, *, report: int, nleds: int) -> None:
        """Initialize BlinkStick state.

        :param report: HID report number for this device variant
        :param nleds: Number of LEDs supported by this device
        """
        self.report = report
        self.nleds = nleds
        self.channel = 0
        self.colors: list[tuple[int, int, int]] = [(0, 0, 0)] * nleds

    def __bytes__(self) -> bytes:
        """Convert state to bytes for device communication.

        Serializes the device state into the format expected by BlinkStick
        devices, including report ID, channel, and LED color data.
        """
        # NOTE: There may be version-specific behavior regarding channel usage
        # This implementation works for tested devices like BlinkStick Square
        buf = [self.report, self.channel]
        for color in self.colors:
            buf.extend(color)
        return bytes(buf)

    @property
    def color(self) -> tuple[int, int, int]:
        """Get the current RGB color of the first lit LED.

        Returns the color of the first LED that has a non-zero color value,
        converted from internal GRB format to standard RGB format.
        """
        for color in self.colors:
            if sum(color) > 0:
                g, r, b = color
                return (r, g, b)
        return (0, 0, 0)

    @staticmethod
    def rgb_to_grb(color: tuple[int, int, int]) -> tuple[int, int, int]:
        """Convert RGB color tuple to internal GRB representation.

        :param color: RGB color tuple (red, green, blue)
        :return: GRB color tuple (green, red, blue)
        """
        r, g, b = color
        return (g, r, b)

    @staticmethod
    def grb_to_rgb(color: tuple[int, int, int]) -> tuple[int, int, int]:
        """Convert internal GRB color tuple to RGB representation.

        :param color: GRB color tuple (green, red, blue)
        :return: RGB color tuple (red, green, blue)
        """
        g, r, b = color
        return (r, g, b)

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        """Set all LEDs to the same RGB color.

        :param value: RGB color tuple to set for all LEDs
        """
        self.colors = [self.rgb_to_grb(value)] * self.nleds

    def get_led(self, index: int) -> tuple[int, int, int]:
        """Get the RGB color of a specific LED.

        :param index: LED index (0-based)
        :return: RGB color tuple, or (0,0,0) if index is invalid
        """
        try:
            return self.grb_to_rgb(self.colors[index])
        except IndexError:
            return (0, 0, 0)

    def set_led(self, index: int, color: tuple[int, int, int]) -> None:
        """Set the RGB color of a specific LED.

        :param index: LED index (0-based)
        :param color: RGB color tuple to set
        """
        with contextlib.suppress(IndexError):
            self.colors[index] = self.rgb_to_grb(color)

"""Luxafor Flag"""

from functools import cached_property
from typing import ClassVar

from .implementation import LEDS, State
from .luxafor_base import LuxaforBase


class Flag(LuxaforBase):
    """Luxafor Flag USB status light with multiple RGB LEDs.

    The Luxafor Flag features six individually controllable RGB LEDs
    arranged in a flag pattern. Use this class to control Flag devices
    for status indication, notifications, or ambient lighting effects.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x4D8, 0xF372): "Flag",
    }

    @cached_property
    def state(self) -> State:
        """Device state manager for controlling Flag LED array.

        Returns a State instance that manages the 6-LED array with individual
        RGB control for each LED position. Use this to modify LED states
        before calling update() to apply changes to hardware.

        :return: State instance for managing all 6 LEDs
        """
        return State()

    @property
    def nleds(self) -> int:
        """The number of individually addressable LEDs."""
        return 6

    def __bytes__(self) -> bytes:
        return bytes(self.state)

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on a Luxafor device with the specified color tuple.

        :param color: RGB color tuple (red, green, blue)
        """
        try:
            leds = LEDS(led)
        except ValueError:
            leds = LEDS.All

        with self.batch_update():
            self.color = color
            try:
                self.state.leds = leds
            except ValueError:
                self.state.leds = leds

    @property
    def color(self) -> tuple[int, int, int]:
        """The current RGB color of a Luxafor device."""
        return self.state.color

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        self.state.color = value

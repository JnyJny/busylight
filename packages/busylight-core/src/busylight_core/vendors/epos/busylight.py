"""EPOS Busylight Support"""

from functools import cached_property
from typing import ClassVar

from .epos_base import EPOSBase
from .implementation import Action, Report, State


class Busylight(EPOSBase):
    """EPOS Busylight status light controller.

    The EPOS Busylight is a USB-connected RGB LED device that provides
    status indication with multiple LED control capabilities.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x1395, 0x0074): "Busylight",
    }

    @cached_property
    def state(self) -> State:
        """The device state manager for controlling LED patterns."""
        return State()

    def __bytes__(self) -> bytes:
        return bytes(self.state)

    @property
    def nleds(self) -> int:
        """The number of individually addressable LEDs."""
        return self.state.nleds

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on the EPOS Busylight with the specified color.

        :param color: RGB color tuple (red, green, blue) with values 0-255
        :param led: LED index (0 for both LEDs, 1 for first LED, 2 for second LED)
        """
        with self.batch_update():
            match led:
                case 1:
                    self.state.color0 = color
                case 2:
                    self.state.color1 = color
                case _:
                    self.state.color = color

            self.state.report = Report.ONE
            self.state.action = Action.SetColor

    @property
    def color(self) -> tuple[int, int, int]:
        """The device color as a tuple of RGB values."""
        return self.state.color

    @color.setter
    def color(self, color: tuple[int, int, int]) -> None:
        self.state.color = color

    def reset(self) -> None:
        """Reset the device to its default state."""
        self.state.clear()
        super().reset()

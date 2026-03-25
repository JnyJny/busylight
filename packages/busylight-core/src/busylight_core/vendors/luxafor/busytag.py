"""BusyTag Light Support"""

from typing import ClassVar

from busylight_core.mixins import ColorableMixin

from ._busytag import Command
from .luxafor_base import LuxaforBase


class BusyTag(ColorableMixin, LuxaforBase):
    """BusyTag status light controller.

    The BusyTag is a wireless status light that uses command strings
    for communication and supports various lighting patterns.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x303A, 0x81DF): "Busy Tag",
    }

    @classmethod
    def claims(cls, hardware) -> bool:
        """Return True if the hardware matches the BusyTag criteria."""
        return super().claims(hardware, product_check=False)

    @property
    def command(self) -> str:
        """Get the current command string for device communication."""
        return getattr(self, "_command", "")

    @command.setter
    def command(self, value: str) -> None:
        self._command = value

    def __bytes__(self) -> bytes:
        return self.command.encode()

    @property
    def nleds(self) -> int:
        """The number of individually addressable LEDs."""
        return 7

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on the BusyTag with the specified color.

        :param color: RGB color tuple (red, green, blue)
        :param led: LED index (default is 0, for all LEDs)
        """
        with self.batch_update():
            self.color = color
            self.command = Command.solid_color(color, led)

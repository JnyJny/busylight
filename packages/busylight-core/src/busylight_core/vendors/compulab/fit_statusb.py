"""CompuLab fit-statUSB status light implementation."""

from typing import ClassVar

from busylight_core.mixins import ColorableMixin

from .compulab_base import CompuLabBase


class FitStatUSB(ColorableMixin, CompuLabBase):
    """CompuLab fit-statUSB status light controller.

    The fit-statUSB is a USB-connected RGB LED device that communicates
    using text-based commands for color control.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x2047, 0x03DF): "fit-statUSB",
    }

    def __bytes__(self) -> bytes:
        buf = f"B#{self.red:02x}{self.green:02x}{self.blue:02x}\n"

        return buf.encode()

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on the fit-statUSB with the specified color.

        :param color: RGB tuple (red, green, blue).
        :param led: LED index (not used by fit-statUSB).
        """
        with self.batch_update():
            self.color = color

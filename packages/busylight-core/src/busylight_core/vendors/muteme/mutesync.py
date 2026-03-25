"""MuteSync status light and button implementation."""

from typing import ClassVar

from busylight_core.hardware import Hardware
from busylight_core.mixins import ColorableMixin

from .muteme_base import MuteMeBase


class MuteSync(ColorableMixin, MuteMeBase):
    """MuteSync status light and button controller.

    The MuteSync is a USB-connected device that combines button
    functionality with status light capabilities for meeting control.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x10C4, 0xEA60): "MuteSync Button",
    }

    @classmethod
    def claims(cls, hardware: Hardware) -> bool:
        """Return True if the hardware describes a MuteSync device."""
        # Addresses busylight-for-humans issue #356 where MuteSync
        # claims another hardware with a SiliconLabs CP2102 USB to
        # Serial controller that is not MuteSync hardware.

        claim = super().claims(hardware)

        try:
            manufacturer = "mutesync" in hardware.manufacturer_string.lower()
        except AttributeError:
            manufacturer = False

        try:
            product = "mutesync" in hardware.product_string.lower()
        except AttributeError:
            product = False

        return claim and (product or manufacturer)

    def __bytes__(self) -> bytes:
        buf = [65] + [*self.color] * 4
        return bytes(buf)

    @property
    def is_button(self) -> bool:
        """True if this device has button functionality."""
        return True

    @property
    def button_on(self) -> bool:
        """True if the mute button is currently pressed."""
        return False

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on the MuteSync with the specified color.

        :param color: RGB color tuple (red, green, blue) with values 0-255
        :param led: LED index (unused for MuteSync)
        """
        with self.batch_update():
            self.color = color

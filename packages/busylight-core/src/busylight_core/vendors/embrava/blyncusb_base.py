"""Embrava early Blynclight (Blyncusb) family base class."""

from typing import TYPE_CHECKING

from .embrava_base import EmbravaBase
from .implementation import snap_color

if TYPE_CHECKING:
    from busylight_core.hardware import Hardware


class BlyncusbBase(EmbravaBase):
    """Base class for early Blynclight devices (VID 0x1130).

    Provides shared behavior for BLYNCUSB10 and BLYNCUSB20 devices
    including palette-based color management and interface claiming.

    These devices only support 7 predefined colors plus OFF. The color
    setter silently maps any RGB input to the nearest palette color,
    so the stored color always reflects what the device is actually
    displaying.
    """

    @classmethod
    def claims(cls, hardware: "Hardware") -> bool:
        """Check if this class can control the given hardware device.

        Early Blynclight devices require interface 1 for control.

        :param hardware: Hardware instance to test for compatibility
        :return: True if this class can control the hardware device
        """
        return (
            hardware.device_id in cls.supported_device_ids
            and hardware.interface_number == 1
        )

    @property
    def color(self) -> tuple[int, int, int]:
        """Tuple of RGB color values.

        Returns the palette color the device is actually displaying,
        not necessarily the exact RGB that was requested.
        """
        try:
            return self._color
        except AttributeError:
            self._color = (0, 0, 0)
            return self._color

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        """Set the RGB color, snapped to the nearest palette color."""
        self._color = snap_color(*value)

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on the device with the specified color.

        The RGB color will be mapped to the nearest available palette color.

        :param color: RGB color tuple (red, green, blue)
        :param led: LED index (not used by this device)
        """
        self.color = color
        self.update()

    def reset(self) -> None:
        """Reset the device to its default state (off)."""
        self._color = (0, 0, 0)
        self.update()

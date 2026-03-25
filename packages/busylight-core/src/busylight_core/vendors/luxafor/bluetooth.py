"""Luxafor Bluetooth"""

from typing import ClassVar

from .flag import Flag


class Bluetooth(Flag):
    """Luxafor Bluetooth status light controller.

    A Bluetooth-enabled version of the Luxafor Flag with the same
    functionality as the USB-connected Flag device.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x4D8, 0xF372): "BT",
    }

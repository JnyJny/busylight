"""Embrava Blynclight Mini Support"""

from typing import ClassVar

from .blynclight_plus import BlynclightPlus


class BlynclightMini(BlynclightPlus):
    """Embrava Blynclight Mini status light controller.

    A smaller version of the Blynclight with the similar functionality
    as the Blynclight Plus device.

    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x2C0D, 0x0003): "Blynclight Mini",
        (0x2C0D, 0x000A): "Blynclight Mini",
        (0x0E53, 0x2517): "Blynclight Mini",
        (0x0E53, 0x2519): "Blynclight Mini",
    }

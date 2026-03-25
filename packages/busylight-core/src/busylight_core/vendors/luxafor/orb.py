"""Luxafor Orb"""

from typing import ClassVar

from .flag import Flag


class Orb(Flag):
    """Luxafor Orb status light controller.

    A spherical-shaped status light with the same functionality
    as the Luxafor Flag device.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x4D8, 0xF372): "Orb",
    }

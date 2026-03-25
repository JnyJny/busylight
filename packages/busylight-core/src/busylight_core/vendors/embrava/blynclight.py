"""Embrava Blynclight Support"""

from typing import ClassVar

from .blynclight_base import BlynclightBase


class Blynclight(BlynclightBase):
    """Embrava Blynclight USB status light for basic visual indication.

    The standard Blynclight provides RGB LED status indication and flashing
    patterns. For audio capabilities, use BlynclightPlus or BlynclightMini.
    Use this class to control basic Blynclight devices for visual-only
    status notifications.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x2C0D, 0x0001): "Blynclight",
        (0x2C0D, 0x000C): "Blynclight",
        (0x0E53, 0x2516): "Blynclight",
    }

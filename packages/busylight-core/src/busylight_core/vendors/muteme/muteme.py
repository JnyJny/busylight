"""MuteMe Button & Light"""

from typing import ClassVar

from .muteme_base import MuteMeBase


class MuteMe(MuteMeBase):
    """MuteMe status light and button controller.

    The MuteMe is a USB-connected RGB LED device with integrated button
    functionality for mute control in video conferencing applications.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x16C0, 0x27DB): "MuteMe Original",
        (0x20A0, 0x42DA): "MuteMe Original",
    }

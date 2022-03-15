"""
"""

from .flag import Flag


class Mute(Flag):

    SUPPORTED_DEVICE_IDS = {
        (0x4D8, 0xF372): "Mute",
    }

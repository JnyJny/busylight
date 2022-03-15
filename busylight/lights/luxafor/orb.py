"""
"""

from .flag import Flag


class Orb(Flag):

    SUPPORTED_DEVICE_IDS = {
        (0x4D8, 0xF372): "Orb",
    }

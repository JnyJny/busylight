"""
"""

from loguru import logger

from .flag import Flag


class Mute(Flag):

    supported_device_ids = {
        (0x4D8, 0xF372): "Mute",
    }

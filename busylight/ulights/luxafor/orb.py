""" Luxafor Orb
"""

from loguru import logger

from .flag import Flag


class Orb(Flag):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0x4D8, 0xF372): "Orb",
        }

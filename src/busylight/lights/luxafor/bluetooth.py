""" Luxafor Bluetooth
"""

from typing import Dict, Tuple

from .flag import Flag


class Bluetooth(Flag):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x4D8, 0xF372): "BT",
        }

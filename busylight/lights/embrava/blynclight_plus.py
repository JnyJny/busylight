"""Embrava Blynclight Plus Support

"""

from typing import Dict, Tuple

from .blynclight import Blynclight


class Blynclight_Plus(Blynclight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x2C0D, 0x0002): "Blynclight Plus",
            (0x2C0D, 0x0010): "Blynclight Plus",
        }

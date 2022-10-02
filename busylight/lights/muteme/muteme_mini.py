""" MuteMe Mini Support
"""

from typing import Dict, Tuple

from .muteme import MuteMe


class MuteMe_Mini(MuteMe):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x20A0, 0x42DB): "MuteMe Mini",
        }

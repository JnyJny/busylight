""" Busylight Omega Support
"""

from typing import Dict, Tuple

from .busylight_alpha import Busylight_Alpha


class Busylight_Omega(Busylight_Alpha):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x27BB, 0x3BCD): "Busylight Omega",
            (0x27BB, 0x3BCF): "Busylight Omega",
        }

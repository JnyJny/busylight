"""Plantronics Status Indicator
"""


from typing import Dict, Tuple

from ..embrava.blynclight import Blynclight


class Status_Indicator(Blynclight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x047F, 0xD005): "Status Indicator",
        }

    @staticmethod
    def vendor() -> str:
        return "Plantronics"

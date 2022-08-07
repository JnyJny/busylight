"""Plantronics Status Indicator
"""


from loguru import logger

from ..embrava.blynclight import Blynclight


class Status_Indicator(Blynclight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0x047F, 0xD005): "Status Indicator",
        }

    @staticmethod
    def vendor() -> str:
        return "Plantronics"

    @property
    def name(self) -> str:
        return self.hidinfo["product_string"]

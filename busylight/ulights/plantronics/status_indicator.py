"""Plantronics Status Indicator
"""


from loguru import logger

from ..embrava.blynclight import Blynclight


class Status_Indicator(Blynclight):

    supported_device_ids = {
        (0x047F, 0xD005): "Status Indicator",
    }

    vendor = "Plantronics"

    @property
    def name(self) -> str:
        return self.hidinfo["product_string"]

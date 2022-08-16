"""Plantronics Status Indicator
"""

from ..embrava.blynclight import Blynclight


class Status_Indicator(Blynclight):

    SUPPORTED_DEVICE_IDS = {
        (0x047F, 0xD005): "Status Indicator",
    }
    vendor = "Plantronics"

    @property
    def name(self) -> str:
        return self.hidinfo["product_string"]

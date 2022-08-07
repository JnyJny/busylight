"""
"""


from loguru import logger

from ..hidlight import HIDLight, HIDInfo


class BlinkStick(HIDLight):

    supported_vendor_ids = {
        (0x20A0, 0x41E5): "BlinkStick",
    }

    vendor = "Agile Innovative"

"""
"""

from loguru import logger

from ..hidlight import HIDLight, HIDInfo


class Busylight(HIDLight):

    supported_device_ids = {
        (0x04D8, 0xF848): "Busylight Alpha",
        (0x27BB, 0x3BCA): "Busylight Alpha",
        (0x27BB, 0x3BCD): "Busylight Omega",
        (0x27BB, 0x3BCF): "Busylight Omega",
    }

    vendor = "Kuando"

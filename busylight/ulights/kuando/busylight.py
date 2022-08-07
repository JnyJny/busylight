"""
"""

from loguru import logger

from ..hidlight import HIDLight, HIDInfo


class Busylight(HIDLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0x04D8, 0xF848): "Busylight Alpha",
            (0x27BB, 0x3BCA): "Busylight Alpha",
            (0x27BB, 0x3BCD): "Busylight Omega",
            (0x27BB, 0x3BCF): "Busylight Omega",
        }

    @staticmethod
    def vendor() -> str:
        return "Kuando"

"""
"""

from loguru import logger

from ..hidlight import HIDLight


class MuteMe(HIDLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0x16C0, 0x27DB): "MuteMe Original (prototype)",
            (0x20A0, 0x42DA): "MuteMe Original",
            (0x20A0, 0x42DB): "MuteMe Mini",
        }

    @staticmethod
    def vendor() -> str:
        return "MuteMe"

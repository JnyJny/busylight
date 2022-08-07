"""
"""

from loguru import logger

from ..hidlight import HIDLight, HIDInfo


class MuteMe(HIDLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {}

    @staticmethod
    def vendor() -> str:
        return "MuteMe"

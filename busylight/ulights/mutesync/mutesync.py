"""
"""

from loguru import logger

from ..seriallight import SerialLight


class MuteSync(SerialLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {}

    @staticmethod
    def vendor() -> str:
        return "MuteSync"

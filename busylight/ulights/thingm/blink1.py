"""
"""

from loguru import logger

from ..hidlight import HIDLight


class Blink1(HIDLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0x27B8, 0x01ED): "Blink(1)",
        }

    @staticmethod
    def vendor() -> str:
        return "ThingM"

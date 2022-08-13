"""
"""


from loguru import logger

from ..hidlight import HIDLight


class BlinkStick(HIDLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0x20A0, 0x41E5): "BlinkStick",
        }

    @staticmethod
    def vendor() -> str:
        return "Agile Innovative"

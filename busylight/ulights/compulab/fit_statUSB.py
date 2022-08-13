"""
"""

from loguru import logger

from ..seriallight import SerialLight, SerialInfo


class Fit_StatUSB(SerialLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0x2047, 0x03df): "fit-statUSB",
        }

    @staticmethod
    def vendor() -> str:
        return "Compulab"

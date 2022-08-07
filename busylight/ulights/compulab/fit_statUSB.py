"""
"""

from loguru import logger

from ..seriallight import SerialLight, SerialInfo


class Fit_StatUSB(SerialLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0, 0): "fit-statUSB",
        }

    @staticmethod
    def vendor() -> str:
        return "Compulab"

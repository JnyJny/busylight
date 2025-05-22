"""
"""

from typing import Dict, Tuple

from loguru import logger

from ..seriallight import SerialLight


class Fit_StatUSB(SerialLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x2047, 0x03DF): "fit-statUSB",
        }

    @staticmethod
    def vendor() -> str:
        return "CompuLab"

    def __bytes__(self) -> bytes:

        buf = f"B#{self.red:02x}{self.green:02x}{self.blue:02x}\n"

        return buf.encode()

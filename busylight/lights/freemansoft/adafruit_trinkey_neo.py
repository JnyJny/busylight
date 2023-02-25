"""
"""

from typing import Dict, Tuple

from loguru import logger

from ..seriallight import SerialLight


class Adafruit_TrinkeyNeo(SerialLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x239A, 0x0080): "Adafruit-TrinkeyNeo",
        }

    @staticmethod
    def vendor() -> str:
        return "Adafruit"

    def __bytes__(self) -> bytes:
        # all pixels
        buf = f"#ff{self.red:02x}{self.green:02x}{self.blue:02x}\n"

        return buf.encode()

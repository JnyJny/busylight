"""
"""

from typing import Dict, Tuple

from loguru import logger

from ..seriallight import SerialLight


class MuteSync(SerialLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x10C4, 0xEA60): "MuteSync Button",
        }

    @staticmethod
    def vendor() -> str:
        return "MuteSync"

    def __bytes__(self) -> bytes:

        buf = [65] + [*self.color] * 4

        return bytes(buf)

    @property
    def is_button(self) -> bool:
        return True

    @property
    def button_on(self) -> bool:
        return False

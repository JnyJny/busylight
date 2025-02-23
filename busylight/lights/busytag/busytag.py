"""
"""

from typing import Dict, Tuple

from loguru import logger

from ..seriallight import SerialLight


class BusyTag(SerialLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x303a, 0x81df): "Busy Tag",
        }

    @staticmethod
    def vendor() -> str:
        return "Busy Tag"

    def __bytes__(self) -> bytes:

        # Change Color using AT Serial Commands 
        # See for reference:
        # https://luxafor.helpscoutdocs.com/article/47-busy-tag-usb-cdc-command-reference-guide
        # AT+SC=127,<hex color>

        buf = f"AT+SC=127,{self.red:02x}{self.green:02x}{self.blue:02x}"

        return buf.encode()

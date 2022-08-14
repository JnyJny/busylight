"""
"""

from loguru import logger

from ..seriallight import SerialLight


class MuteSync(SerialLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0x10C4, 0xEA60): "MuteSync Button",
        }

    @staticmethod
    def vendor() -> str:
        return "MuteSync"

    def __bytes__(self) -> bytes:
        return bytes()

    @property
    def red(self) -> int:
        return getattr(self, "_red", 0)

    @red.setter
    def red(self, new_value: int) -> int:
        self._red = new_value

    @property
    def green(self) -> int:
        return getattr(self, "_green", 0)

    @green.setter
    def green(self, new_value: int) -> int:
        self._green = new_value

    @property
    def blue(self) -> int:
        return getattr(self, "_blue", 0)

    @blue.setter
    def blue(self, new_value: int) -> int:
        self._blue = new_value

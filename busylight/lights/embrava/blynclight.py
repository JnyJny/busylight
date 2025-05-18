""" Embrava Blynclight Support
"""

from typing import Dict, Tuple

from ..hidlight import HIDLight
from ..light import LightInfo

from ._blynclight import Command


class Blynclight(HIDLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x2C0D, 0x0001): "Blynclight",
            (0x2C0D, 0x000C): "Blynclight",
            (0x0E53, 0x2516): "Blynclight",
        }

    @staticmethod
    def vendor() -> str:
        return "Embrava"

    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:

        self.command = Command()

        super().__init__(light_info, reset=reset, exclusive=exclusive)

    def on(self, color: Tuple[int, int, int]) -> None:

        with self.batch_update():
            self.command.off = 0
            self.color = color

    @property
    def red(self) -> int:
        return self.command.red

    @red.setter
    def red(self, new_value: int) -> None:
        self.command.red = new_value

    @property
    def green(self) -> int:
        return self.command.green

    @green.setter
    def green(self, new_value: int) -> None:
        self.command.green = new_value

    @property
    def blue(self) -> int:
        return self.command.blue

    @blue.setter
    def blue(self, new_value: int) -> None:
        self.command.blue = new_value

    def __bytes__(self) -> bytes:
        return self.command.bytes

    def reset(self) -> None:
        with self.batch_update():
            self.command.reset()

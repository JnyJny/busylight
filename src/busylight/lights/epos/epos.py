""" EPOS Busylight Support
"""

from typing import Callable, Dict, Tuple

from loguru import logger

from ..hidlight import HIDLight
from ..light import LightInfo

from ._epos import Command


class EPOSBusylight(HIDLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x1395, 0x0074): "Busylight",
        }

    @staticmethod
    def vendor() -> str:
        return "EPOS"

    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:

        self.command = Command()

        super().__init__(light_info, reset=reset, exclusive=exclusive)

    def __bytes__(self) -> bytes:

        return self.command.bytes

    def on(self, color: Tuple[int, int, int]) -> None:
        with self.batch_update():
            self.command.set_color(color)

    def reset(self) -> None:
        with self.batch_update():
            self.command.reset()

    @property
    def red(self) -> int:
        return self.command.red

    @red.setter
    def red(self, new_value: int) -> None:
        self.command.red1 = self.command.red2 = new_value

    @property
    def green(self) -> int:
        return self.command.green

    @green.setter
    def green(self, new_value: int) -> None:
        self.command.green1 = self.command.green2 = new_value

    @property
    def blue(self) -> int:
        return self.command.blue

    @blue.setter
    def blue(self, new_value: int) -> None:
        self.command.blue1 = self.command.blue2 = new_value

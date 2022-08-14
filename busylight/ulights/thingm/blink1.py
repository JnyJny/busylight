""" ThingM blink(1)
"""

from typing import Callable, Tuple

from loguru import logger

from ..hidlight import HIDLight
from ..light import LightInfo

from ._blink1 import Command


class Blink1(HIDLight):
    @staticmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        return {
            (0x27B8, 0x01ED): "Blink(1)",
        }

    @staticmethod
    def vendor() -> str:
        return "ThingM"

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
            self.command.fade_to_color(color)

    def reset(self) -> None:
        with self.batch_update():
            self.command.reset()

    @property
    def write_strategy(self) -> Callable:
        return self.device.send_feature_report

    @property
    def red(self) -> int:
        return self.command.red

    @red.setter
    def red(self, new_value: int) -> int:
        self.command.red = new_value

    @property
    def green(self) -> int:
        return self.command.green

    @green.setter
    def green(self, new_value: int) -> int:
        self.command.green = new_value

    @property
    def blue(self) -> int:
        return self.command.blue

    @blue.setter
    def blue(self, new_value: int) -> int:
        self.command.blue = new_value

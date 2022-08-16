""" ThingM Blink(1)
"""

from typing import Callable

from loguru import logger

from ...color import ColorTuple

from ..speed import Speed
from ..usblight import USBLight, HidInfo

from .blink1_impl import Command


class Blink1(USBLight):
    SUPPORTED_DEVICE_IDS = {
        (0x27B8, 0x01ED): "Blink(1)",
    }
    vendor = "ThingM"

    def __init__(
        self,
        hidinfo: HidInfo,
        reset: bool = True,
    ) -> None:
        self.command = Command()
        super().__init__(hidinfo, reset=reset)

    @property
    def write_strategy(self) -> Callable:
        return self.device.send_feature_report

    def __bytes__(self) -> bytes:

        return self.command.bytes

    def on(self, color: ColorTuple) -> None:

        with self.batch_update():
            super().on(color)
            self.command.fade_to_color(color)

    def blink(self, color: ColorTuple, blink: Speed = Speed.Slow) -> None:

        activate = 10
        decay = 100 // (blink.rate + 1)

        self.command.write_pattern_line(color, activate, 0)
        self.update()

        self.command.write_pattern_line((0, 0, 0), decay, 1)
        self.update()

        self.command.save_patterns()
        self.update()

        self.command.play_loop(1, 0, 1)
        self.update()

    def off(self) -> None:
        self.on((0, 0, 0))
        super().off()

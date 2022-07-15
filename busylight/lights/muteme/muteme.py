""" MuteMe 
"""

from loguru import logger

from ...color import ColorTuple

from ..exceptions import LightUnsupported
from ..speed import Speed
from ..usblight import USBLight, HidInfo

from .muteme_impl import Command


class MuteMe(USBLight):
    SUPPORTED_DEVICE_IDS = {
        (0x16C0, 0x27DB): "MuteMe Original (prototype)",
        (0x20A0, 0x42DA): "MuteMe Original",
        (0x20A0, 0x42DB): "MuteMe Mini",
    }
    vendor = "MuteMe"

    def __init__(
        self,
        hidinfo: HidInfo,
        reset: bool = True,
    ) -> None:
        self.command = Command()
        super().__init__(hidinfo, reset=reset)

    def __bytes__(self) -> bytes:
        return self.command.bytes

    def on(self, color: ColorTuple) -> None:
        super().on(color)
        with self.batch_update():
            self.command.color = self.color

    def off(self) -> None:
        self.on((0, 0, 0))
        super().off()

    def blink(self, color: ColorTuple, blink: Speed = Speed.Slow) -> None:
        super().blink(color, blink)
        with self.batch_update():
            self.command.color = color
            self.command.blink = blink.value & 0x2

    @property
    def touch(self) -> int:
        """ """
        raise NotImplementedError("touch")

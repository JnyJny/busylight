""" Embrava BlyncLight Family
"""
from loguru import logger

from ...color import ColorTuple

from ..speed import Speed
from ..usblight import USBLight, HidInfo

from .blynclight_impl import BlynclightCommand


class Blynclight(USBLight):

    SUPPORTED_DEVICE_IDS = {
        (0x2C0D, 0x0001): "Blynclight",
        (0x2C0D, 0x000A): "Blynclight Mini",
        (0x2C0D, 0x000C): "Blynclight",
        (0x2C0D, 0x0010): "Blynclight Plus",
        (0x0E53, 0x2517): "Blynclight Mini",
        (0x0E53, 0x2516): "Blynclight"
    }
    vendor = "Embrava"

    def __init__(
        self,
        hidinfo: HidInfo,
        reset: bool = True,
    ) -> None:
        self.command = BlynclightCommand()
        super().__init__(hidinfo, reset=reset)

    def __bytes__(self) -> bytes:
        self.command.color = self.color
        return self.command.bytes

    def on(self, color: ColorTuple) -> None:

        super().on(color)

        with self.batch_update():
            self.command.off = 1 if color == (0, 0, 0) else 0
            self.command.flash = 0
            self.command.speed = 1

    def blink(self, color: ColorTuple, blink: Speed = Speed.Slow) -> None:
        with self.batch_update():
            self.color = color
            self.command.flash = 1
            self.command.speed = 1 << (blink.rate - 1)

    def off(self) -> None:
        self.on((0, 0, 0))
        super().off()

    def reset(self) -> None:
        self.command.reset()
        super().reset()

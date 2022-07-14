"""
"""

from loguru import logger

from ...color import ColorTuple

from ..exceptions import LightUnsupported
from ..speed import Speed
from ..usblight import USBLight, HidInfo

from .muteme_impl import MuteMeColor, MuteMeUnknownColor


class MuteMe(USBLight):
    SUPPORTED_DEVICE_IDS = {
        (0x20A0, 0x42DA): "MuteMe",
    }
    vendor = "MuteMe"

    @property
    def command(self) -> list[int]:
        try:
            return self._command
        except AttributeError:
            pass
        self._command = [0x00, 0x00]
        return self._command

    def __bytes__(self) -> bytes:
        return bytes(self.command[:2])

    def on(self, color: ColorTuple) -> None:
        super().on(color)
        with self.batch_update():
            try:
                self.command[1] = MuteMeColor.from_colortuple(color).value
            except MuteMeUnknownColor as error:
                logger.info(str(error))

    def off(self) -> None:
        self.on((0, 0, 0))
        super().off()

    def blink(self, color: ColorTuple, blink: Speed = Speed.Slow) -> None:
        logger.info(f"{color=} {blink=}")

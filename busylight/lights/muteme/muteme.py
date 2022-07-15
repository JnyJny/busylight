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
            if blink in [Speed.Slow, Speed.Medium]:
                self.command.blink = 2
            if blink in [Speed.Fast]:
                self.command.blink = 1

    def touch(self, timeout: int = 100) -> bool:
        """Returns the current state of the touch surface."""

        # EJO this is a hack constructed from observing that
        #     consecutive reads from the device while touched can be:
        #
        #     a = [0, 0, 0, 1]
        #     b = [0, 0, 0, 0]
        #
        #     Sometimes the order is reversed where b contains the
        #     actual touch status in the final byte. If we sum each of
        #     the items in both arrays we should arrive at a valid
        #     touch status in the final byte regardless of how the
        #     device was polled. This behavior will probably need to
        #     be controlled, hopefully the device release_number will
        #     provide the necessary information to differentiate
        #     devices that might need different polling strategies.
        #

        first = self.read_strategy(4, timeout)
        second = self.read_strategy(4, timeout)

        result = [f + s for f, s in zip(first, second)]

        try:
            return result[-1] == 1
        except IndexError:
            pass
        return False

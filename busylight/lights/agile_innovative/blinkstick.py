"""Agile Innovative BlinkStick
"""

import asyncio

from typing import Awaitable, Dict, List, Optional

from ...color import ColorTuple

from ..exceptions import LightUnsupported
from ..speed import Speed
from ..usblight import USBLight, HidInfo

from .blinkstick_impl import BlinkStickType, Report


class BlinkStick(USBLight):

    SUPPORTED_DEVICE_IDS = {
        (0x20A0, 0x41E5): "BlinkStick",
    }

    vendor = "Agile Innovative"

    @classmethod
    def claims(cls, hidinfo: HidInfo) -> bool:

        if not super().claims(hidinfo):
            return False

        try:
            BlinkStickType.from_dict(hidinfo)
            return True
        except LightUnsupported:
            pass
        return False

    @classmethod
    def supported_lights(cls) -> Dict[str, List[str]]:
        return {cls.vendor: [device.name for device in BlinkStickType]}

    def __init__(
        self,
        hidinfo: HidInfo,
        reset: bool = True,
    ) -> None:
        self.channel = 0
        self.index = 0
        self._blinkstick_type = BlinkStickType.from_dict(hidinfo)
        super().__init__(hidinfo, reset=reset)

    @property
    def blinkstick_type(self) -> BlinkStickType:
        return getattr(self, "_blinkstick_type")

    @property
    def name(self) -> str:
        if self.blinkstick_type == BlinkStickType.BlinkStick:
            return "BlinkStick"
        return self.blinkstick_type.name.title()

    @property
    def report(self) -> int:
        return self.blinkstick_type.report

    @property
    def nleds(self) -> int:
        return self.blinkstick_type.nleds

    def __bytes__(self) -> bytes:

        # blinkstick color order is GRB
        #
        # To keep the interface consistent, self.color is kept in RGB
        # order and the order isn't transposed until it's time to
        # write to the device and `bytes(self)` is called in the
        # USBLight.strategy method.

        r, g, b = self.color

        if self.report == Report.Single:
            return bytes([self.report, g, r, b])

        buf = [self.report, self.channel]
        buf.extend([g, r, b] * self.nleds)

        return bytes(buf)

    def on(self, color: ColorTuple) -> None:
        with self.batch_update():
            super().on(color)

    def blink(self, color: ColorTuple, speed: Speed = Speed.Slow) -> None:

        raise NotImplementedError("blink")

    def off(self):
        self.on((0, 0, 0))
        super().off()

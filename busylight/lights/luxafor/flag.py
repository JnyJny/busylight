""" Luxafor Flag
"""
from loguru import logger

from ...color import ColorTuple

from ..exceptions import LightUnsupported
from ..speed import Speed
from ..usblight import USBLight, HidInfo

from .flag_impl import LEDS, Wave, Pattern, Command


class Flag(USBLight):

    SUPPORTED_DEVICE_IDS = {
        (0x4D8, 0xF372): "Flag",
    }
    vendor = "Luxafor"

    _base_strobe = 0x20

    @classmethod
    def claims(cls, hidinfo: HidInfo) -> bool:

        if not super().claims(hidinfo):
            return False
        try:
            product = hidinfo["product_string"].split()[-1].casefold()
        except (KeyError, IndexError) as error:
            logger.debug(f"problem {error} processing {hidinfo}")
            return False

        return product in map(str.casefold, cls.SUPPORTED_DEVICE_IDS.values())

    def __init__(
        self,
        hidinfo: HidInfo,
        reset: bool = True,
    ) -> None:
        self.cmd = Command.Color
        self.leds = LEDS.All
        self.fade = 0
        self.repeat = 0
        super().__init__(hidinfo, reset=reset)

    def __bytes__(self) -> bytes:

        # EJO The Flag's command structure is all byte aligned with no
        #     sub-byte or byte-crossing fields, so there's no need to
        #     use BitVector when a list of byte values will do the
        #     job.

        if self.cmd not in [Command.Color, Command.Strobe]:
            # EJO add support for other commands as time permits.
            raise NotImplementedError(f"Flag command {self.cmd} not implemented")

        if self.cmd in [Command.Color, Command.Fade]:
            data = [self.cmd, self.leds, *self.color, self.fade, self.repeat]

        if self.cmd == Command.Strobe:
            data = [self.cmd, self.leds, *self.color, self.speed, 0, self.repeat]

        return bytes(data)

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            pass
        self._name = self.hidinfo["product_string"].title()
        return self._name

    def on(self, color: ColorTuple) -> None:

        with self.batch_update():
            super().on(color)
            self.cmd = Command.Color

    def blink(self, color: ColorTuple, blink: Speed = Speed.Slow) -> None:
        with self.batch_update():
            self.cmd = Command.Strobe
            self.speed = int(self._base_strobe // blink.rate)

    def off(self) -> None:
        self.on((0, 0, 0))
        super().off()

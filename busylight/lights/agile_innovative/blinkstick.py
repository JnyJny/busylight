""" Agile Innovative BlinkStick
"""


from typing import Dict, Tuple

from loguru import logger

from ..hidlight import HIDLight
from ..light import LightInfo

from ._blinkstick import BlinkStickType, Report


class BlinkStick(HIDLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x20A0, 0x41E5): "BlinkStick",
        }

    @staticmethod
    def vendor() -> str:
        return "Agile Innovative"

    def __init__(
        self, light_info: LightInfo, reset: bool = True, exclusive: bool = True
    ) -> None:

        self.channel = 0
        self.index = 0
        self._device_type = BlinkStickType.from_dict(light_info)

        super().__init__(light_info, reset=reset, exclusive=exclusive)

    @property
    def device_type(self) -> BlinkStickType:
        return self._device_type

    @property
    def report(self) -> int:
        return self.device_type.report

    @property
    def nleds(self) -> int:
        return self.device_type.nleds

    @property
    def name(self) -> str:

        if self.device_type == BlinkStickType.BlinkStick:
            return "BlinkStick"
        return self.device_type.name.title()

    def __bytes__(self) -> bytes:

        if self.report == Report.Single:
            return bytes([self.report, self.green, self.red, self.blue])

        buf = [self.report, self.channel]
        buf.extend([self.green, self.red, self.blue] * self.nleds)

        return bytes(buf)

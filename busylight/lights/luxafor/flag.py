""" Luxafor Flag
"""

from typing import Dict, Tuple

from loguru import logger

from ..hidlight import HIDLight
from ..light import LightInfo

from ._flag import Command, LEDS, Pattern, Wave


class Flag(HIDLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x4D8, 0xF372): "Flag",
        }

    @staticmethod
    def vendor() -> str:
        return "Luxafor"

    @classmethod
    def claims(cls, light_info: LightInfo) -> bool:

        if not super().claims(light_info):
            return False

        try:
            product = light_info["product_string"].split()[-1].casefold()
        except (KeyError, IndexError) as error:
            logger.debug(f"problem {error} processing {light_info}")
            return False

        return product in map(str.casefold, cls.supported_device_ids().values())

    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:

        self.command = Command.Color
        self.leds = LEDS.All
        self.fade = 0
        self.repeat = 0
        self.pattern = Pattern.Off
        self.wave = Wave.Off

        super().__init__(light_info, reset=reset, exclusive=exclusive)

    def __bytes__(self) -> bytes:

        if self.command in [Command.Color, Command.Fade]:
            data = [
                self.command,
                self.leds,
                self.red,
                self.green,
                self.blue,
                self.fade,
                self.repeat,
            ]
            return bytes(data)

        raise NotImplementedError(self.command)

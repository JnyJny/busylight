"""
"""

from typing import Any, Union

import hid

from loguru import logger


from .light import Light, LightInfo


class HIDLight(Light):
    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not HIDLight

    @classmethod
    def available_lights(cls) -> list[LightInfo]:
        available = [hidinfo for hidinfo in hid.enumerate() if cls.claims(hidinfo)]
        logger.debug(f"{cls} found {len(available)}")
        return available

    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:
        """ """
        logger.debug(f"{light_info}")
        self.info = dict(light_info)
        for key, value in self.info.items():
            setattr(self, key, value)

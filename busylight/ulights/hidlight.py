"""
"""

from typing import Any, Union

import hid

from loguru import logger


from .light import Light, LightInfo


HIDInfo = dict[str, Union[bytes, str, int]]


class HIDLight(Light):
    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not HIDLight

    @classmethod
    def available_lights(cls) -> list[LightInfo]:
        available = [hidinfo for hidinfo in hid.enumerate() if cls.claims(hidinfo)]
        logger.debug(f"{cls} found {len(available)}")
        return available

    @classmethod
    def from_info(cls, info: LightInfo) -> "HIDLight":
        raise NotImplementedError("from_info")

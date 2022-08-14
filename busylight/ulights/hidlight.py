"""
"""

from typing import Any, Dict, List, Union

import hid

from loguru import logger


from .light import Light, LightInfo


class HIDLight(Light):
    @classmethod
    def _is_concrete(cls) -> bool:
        return cls is not HIDLight

    @classmethod
    def available_lights(cls) -> List[LightInfo]:

        available = []
        for hidinfo in hid.enumerate():
            if not cls.claims(hidinfo):
                continue
            info = dict(hidinfo)
            try:
                info["device_id"] = (info["vendor_id"], info["product_id"])
            except KeyError as error:
                logger.error(f"broken HID info {hidinfo}: {error}")
                continue
            available.append(info)

        logger.info(f"{cls} found {len(available)}")
        return available

    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:
        """ """

        super().__init__(light_info, reset=reset, exclusive=exclusive)

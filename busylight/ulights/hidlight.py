"""
"""

from typing import Any, Union

import hid

from loguru import logger


from .light import Light, LightInfo


HIDInfo = dict[str, Union[bytes, str, int]]


class HIDLight(Light):
    @classmethod
    def available_lights(cls) -> list[LightInfo]:
        return [hidinfo for hidinfo in hid.enumerate() if cls.claims(hidinfo)]

    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not HIDLight

    @classmethod
    def claims(cls, light_info: LightInfo) -> bool:

        if cls.is_abstract():
            for subclass in cls.subclasses():
                if subclass.claims(light_info):
                    return True
            return False

        try:
            device_id = (light_info["vendor_id"], light_info["product_id"])
        except KeyError as error:
            logger.error(f"missing keys {error} from light_info {light_info}")
            raise InvalidLightInfo(light_info)

        logger.debug(f"{cls} {cls.supported_device_ids()}")

        return device_id in cls.supported_device_ids()

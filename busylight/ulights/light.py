""" USB Connected Light
"""

import abc
import asyncio

from functools import lru_cache
from typing import Any, TypeVar

from loguru import logger

from .baselight import BaseLight
from .exceptions import LightNotFound, LightUnavailable, LightUnsupported, NoLightsFound
from .taskable import Taskable


LightType = TypeVar("Light")

LightInfo = dict[Any, Any]


class Light(BaseLight, Taskable):
    """ """

    @classmethod
    @lru_cache
    def subclasses(cls) -> list[LightType]:
        """Return a list of concrete Light subclasses."""

        subclasses = []

        for subclass in cls.__subclasses__():
            if subclass.is_concrete():
                subclasses.append(subclass)
            subclasses.extend(subclass.subclasses())

        return subclasses

    @classmethod
    def supported_lights(cls) -> dict[str, list[str]]:
        """Returns a dictionary of supported light names by vendor name."""

        supported_lights = {}
        for subclass in cls.subclasses():
            supported_lights[subclass.vendor()] = list(
                set(subclass.supported_device_ids().values())
            )
        return supported_lights

    @classmethod
    def available_lights(cls) -> list[LightInfo]:
        """Returns a list of dictionaries describing currently available lights."""

        available_lights = []

        for subclass in cls.__subclasses__():
            available_lights.extend(subclass.available_lights())

        logger.info(f"{cls} found {len(available_lights)} total")
        return available_lights

    @classmethod
    def claims(cls, light_info: LightInfo) -> bool:
        """Returns True if the light described by light_info is claimed by this class."""

        if cls.is_abstract():
            for subclass in cls.subclasses():
                if subclass.claims(light_info):
                    return True
            return False
        try:
            device_id = (light_info["vendor_id"], light_info["product_id"])
        except KeyError as error:
            logger.error(f"missing keys {error} from light_info {light_info}")
            raise InvalidLightInfo(light_info) from None

        return device_id in cls.supported_device_ids()

    @classmethod
    def all_lights(cls, reset: bool = True, exclusive: bool = True) -> list["Light"]:
        """Returns a list of all lights found."""

        all_lights = []

        if cls.is_abstract():
            for subclass in cls.subclasses():
                all_lights.extend(subclass.all_lights(reset=reset, exclusive=exclusive))
            logger.info(f"{cls.__name__} found {len(all_lights)} lights total.")
            return all_lights

        for light_info in cls.available_lights():
            try:
                all_lights.append(cls(light_info, reset=reset, exclusive=exclusive))
            except LightUnavailable as error:
                logger.error(f"{cls.__name__} {error}")

        logger.info(f"{cls.__name__} found {len(all_lights)} lights.")
        return all_lights

    @classmethod
    def first_light(cls, reset: bool = True) -> "Light":
        """Returns the first available light."""

        for subclass in cls.subclasses():
            logger.debug(f"{subclass.__name__}")
            for light_info in subclass.available_lights():
                try:
                    return subclass(light_info, reset=reset)
                except LightUnavailable as error:
                    logger.error(f"{subclass.__name__} {error}")
                    raise

        raise NoLightsFound()

    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not Light

    @classmethod
    def is_abstract(cls) -> bool:
        return not cls.is_concrete()

    @staticmethod
    @abc.abstractmethod
    def supported_device_ids() -> dict[tuple[int, int], str]:
        """A dictionary  of device identfiers support by this class.

        Keys are a 2-tuple of vendor_id and product id, values are the
        marketing name associated with that device.
        """

    @staticmethod
    @abc.abstractmethod
    def vendor() -> str:
        """Device vendor name."""

    @abc.abstractmethod
    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:
        """"""

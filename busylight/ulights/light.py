""" USB Connected Light
"""

import abc
import asyncio

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
    def subclasses(cls) -> list[LightType]:
        """Return a list of concrete Light subclasses."""

        subclasses = []

        for subclass in cls.__subclasses__():
            logger.debug(f"{subclass.is_concrete()} {subclass} ")
            if subclass.is_concrete():
                subclasses.append(subclass)
            subclasses.extend(subclass.subclasses())

        return subclasses

    @classmethod
    def supported_lights(cls) -> dict[str, list[str]]:
        """Returns a dictionary of supported light names by vendor name."""

    @classmethod
    def available_lights(cls) -> list[LightInfo]:
        """Returns a list of dictionaries describing currently available lights."""

        available_lights = []
        for subclass in cls.__subclasses__():
            logger.info(f"{subclass}")
            available_lights.extend(subclass.available_lights())
        return available_lights

    @classmethod
    def all_lights(cls) -> list["Light"]:
        """Returns a list of all lights found."""

    @classmethod
    def first_light(cls) -> "Light":
        """Returns the first available light."""

    @classmethod
    def from_dict(cls, light_info: LightInfo, reset: bool = True) -> "Light":
        """Returns a Light configured with the supplied dictionary.

        :param dict: dict[Any, Any]
        :param reset: bool
        :return: a Light subclass
        """
        for subclass in cls.subclasses():
            if subclass.is_concrete():
                try:
                    return cls.from_dict(light_info, reset=reset)
                except LightUnsupported as error:
                    logger.info(f"{cls} {error}")
            else:
                subclass.from_dict(light_info, reset=reset)

        raise LightUnsupported()

    @classmethod
    @abc.abstractmethod
    def claims(cls, light_info: LightInfo) -> bool:
        """Returns True if the supplied dictionary is recognized."""

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
    def __init__(self, light_info: LightInfo, reset: bool = True) -> None:
        """"""

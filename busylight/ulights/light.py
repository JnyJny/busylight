"""
"""

import abc
import asyncio

from typing import Any, TypeVar

from loguru import logger

from .baselight import BaseLight
from .exceptions import LightNotFound, LightUnavailable, LightUnsupported, NoLightsFound
from .taskable import Taskable


LightType = TypeVar("Light")


class Light(BaseLight, Taskable):
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
    def available_lights(cls) -> list[dict[Any, Any]]:
        """Returns a list of dictionaries describing currently available lights."""

        available_lights = []
        if cls.is_concrete:
            pass
        else:
            for subclass in cls.subclasses():
                available_lights.extend(subclass.available_lights())
        return available_lights

    @classmethod
    def all_lights(cls) -> list["Light"]:
        """Returns a list of all lights found."""

    @classmethod
    def first_light(cls) -> "Light":
        """Returns the first available light."""

    @classmethod
    def from_dict(cls, info: dict[Any, Any], reset: bool = True) -> "Light":
        """Returns a Light configured with the supplied dictionary.

        :param dict: dict[Any, Any]
        :param reset: bool
        :return: a Light subclass
        """
        for subclass in self.subclasses():
            try:
                return cls.from_dict(info, reset=reset)
            except LightUnsupported as error:
                logger.info(error)

        raise LightUnsupported()

    @classmethod
    @abc.abstractmethod
    def claims(cls, light_info: dict[Any, Any]) -> bool:
        """Returns True if the supplied dictionary is recognized."""

    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not Light

    @property
    @abc.abstractmethod
    def supported_device_ids(self) -> dict[tuple[int, int], str]:
        """A dictionary  vendor_id/product_id tuples identifying
        device marketing names."""

    @property
    @abc.abstractmethod
    def vendor(self) -> str:
        """The vendor name associated with this light."""

    @abc.abstractmethod
    def __init__(self, light_info: dict[Any, Any], reset: bool = True) -> None:
        """"""

""" USB Connected Light
"""

import abc
import asyncio

from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Callable, Generator, Dict, List, Tuple, Union, TypeVar

from loguru import logger

from .exceptions import LightNotFound, LightUnavailable, LightUnsupported, NoLightsFound
from .taskable import TaskableMixin


LightType = TypeVar("Light")
LightInfo = Dict[str, Union[bytes, int, str]]


class Light(abc.ABC, TaskableMixin):
    """ """

    @classmethod
    @lru_cache
    def subclasses(cls) -> List[LightType]:
        """Return a list of concrete Light subclasses."""

        subclasses = []

        for subclass in cls.__subclasses__():
            if subclass._is_concrete():
                subclasses.append(subclass)
            subclasses.extend(subclass.subclasses())

        return subclasses

    @classmethod
    def supported_lights(cls) -> Dict[str, List[str]]:
        """Returns a dictionary of supported light names by vendor name."""

        supported_lights = {}
        for subclass in cls.subclasses():
            supported_lights[subclass.vendor()] = list(
                set(subclass.supported_device_ids().values())
            )
        return supported_lights

    @classmethod
    def available_lights(cls) -> List[LightInfo]:
        """Returns a list of dictionaries describing currently available lights."""

        available_lights = []

        for subclass in cls.__subclasses__():
            available_lights.extend(subclass.available_lights())

        logger.info(f"{cls} found {len(available_lights)} total")
        return available_lights

    @classmethod
    def claims(cls, light_info: LightInfo) -> bool:
        """Returns True if the light described by light_info is claimed by this class."""

        if cls._is_abstract():
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
    def all_lights(cls, reset: bool = True, exclusive: bool = True) -> List["Light"]:
        """Returns a list of all lights found."""

        all_lights = []

        if cls._is_abstract():
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
    def first_light(cls, reset: bool = True, exclusive: bool = True) -> "Light":
        """Returns the first available light."""

        for subclass in cls.subclasses():
            logger.debug(f"{subclass.__name__}")
            for light_info in subclass.available_lights():
                try:
                    return subclass(light_info, reset=reset, exclusive=exclusive)
                except LightUnavailable as error:
                    logger.error(f"{subclass.__name__} {error}")
                    raise

        raise NoLightsFound()

    @classmethod
    def _is_concrete(cls) -> bool:
        return cls is not Light

    @classmethod
    def _is_abstract(cls) -> bool:
        return not cls._is_concrete()

    @staticmethod
    @abc.abstractmethod
    def supported_device_ids() -> Dict[tuple[int, int], str]:
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
        try:
            if light_info["device_id"] not in self.supported_device_ids():
                raise LightUnsupported(light_info)
        except KeyError:
            raise InvalidLightInfo(light_info)

        self.info = dict(light_info)
        for key, value in self.info.items():
            setattr(self, key, value)
        self._reset = reset
        self._exclusive = exclusive

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(..., reset={self._reset}, exclusive={self._exclusive})"

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            pass
        self._name = self.supported_device_ids()[self.device_id]
        return self._name

    def on(self, color: Tuple[int, int, int]) -> None:
        """Turn the light on with the supplied color tuple."""
        self.color = color

    def off(self) -> None:
        """Turn the light off."""
        self.on((0, 0, 0))

    def reset(self) -> None:
        """Turn off the light and cancel any animation tasks."""
        self.off()
        self.cancel_tasks()

    @property
    def is_pluggedin(self) -> bool:
        """True if the light is plugged in and responding to commands."""
        try:
            results = self.read_strategy(8, timeout_ms=100)
            return True
        except OSError:
            pass
        return False

    @property
    def is_unplugged(self) -> bool:
        """True if the light is not accessible."""
        return not self.is_pluggedin

    @property
    def is_on(self) -> bool:
        return any(self.color)

    @property
    def is_off(self) -> bool:
        return not self.is_on

    @property
    def color(self) -> Tuple[int, int, int]:
        """A three channel color value in RGB order."""
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, new_value: Tuple[int, int, int]) -> None:
        self.red, self.green, self.blue = new_value

    @property
    def red(self) -> int:
        """Red intensity value."""
        return gettattr(self, "_red", 0)

    @property
    def green(self) -> int:
        """Green intensity value."""
        return gettattr(self, "_green", 0)

    @property
    def blue(self) -> int:
        """Blue intensity value."""
        return gettattr(self, "_blue", 0)

    @red.setter
    @abc.abstractmethod
    def red(self, new_red: int) -> None:
        """ """

    @green.setter
    @abc.abstractmethod
    def green(self, new_green: int) -> None:
        """ """

    @blue.setter
    @abc.abstractmethod
    def blue(self, new_blue: int) -> None:
        """ """

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset the light to a known state."""

    @property
    @abc.abstractmethod
    def read_strategy(self) -> Callable:
        """The read function used to communicate with the device."""

    @property
    @abc.abstractmethod
    def write_strategy(self) -> Callable:
        """The write function used to communicate with the device."""

    @abc.abstractmethod
    def acquire(self, exclusive: bool = True) -> None:
        """ """

    @abc.abstractmethod
    def release(self) -> None:
        """ """

    @abc.abstractmethod
    def update(self) -> None:
        """ """

    @contextmanager
    @abc.abstractmethod
    def batch_update(self) -> Generator[None, None, None]:
        """ """

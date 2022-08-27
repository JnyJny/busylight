""" USB Connected Light
"""

import abc
import asyncio

from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Callable, Generator, Dict, List, Tuple, Union, TypeVar

from loguru import logger

from .exceptions import (
    InvalidLightInfo,
    LightNotFound,
    LightUnavailable,
    LightUnsupported,
    NoLightsFound,
)

from .taskable import TaskableMixin


LightType = TypeVar("Light")
LightInfo = Dict[str, Union[bytes, int, str]]


class Light(abc.ABC, TaskableMixin):
    """A USB connected device implementing a light, indicator lamp or button."""

    @classmethod
    @lru_cache(maxsize=None)
    def subclasses(cls) -> List[LightType]:
        """Return a list of Light subclasses implementing support for a physical light."""

        subclasses = []

        for subclass in cls.__subclasses__():
            if subclass._is_concrete():
                subclasses.append(subclass)
            subclasses.extend(subclass.subclasses())

        return subclasses

    @classmethod
    def supported_lights(cls) -> Dict[str, List[str]]:
        """Returns a dictionary of supported light names organized by vendor."""

        supported_lights = {}
        for subclass in cls.subclasses():
            supported_lights[subclass.vendor()] = list(
                set(subclass.supported_device_ids().values())
            )
        return supported_lights

    @classmethod
    def available_lights(cls) -> List[LightInfo]:
        """Returns a list of dictionaries describing currently available lights."""

        # Note: Light's subclasses, HIDLight and SerialLight for now,
        #       are expected to implement device-specific
        #       available_light classmethods.

        available_lights = []

        for subclass in cls.__subclasses__():
            available_lights.extend(subclass.available_lights())

        logger.info(f"{cls} found {len(available_lights)} total")
        return available_lights

    @classmethod
    def claims(cls, light_info: LightInfo) -> bool:
        """Returns True if the light described by light_info is claimed by this class.

        Raises:
        busylight.lights.exceptions.InvalidLightInfo
        """

        if cls._is_abstract():
            for subclass in cls.subclasses():
                if subclass.claims(light_info):
                    return True
            return False

        try:
            return light_info["device_id"] in cls.supported_device_ids()
        except KeyError as error:
            logger.error(f"missing keys {error} from light_info {light_info}")
            raise InvalidLightInfo(light_info) from None

    @classmethod
    def all_lights(cls, reset: bool = True, exclusive: bool = True) -> List["Light"]:
        """Returns a list of all lights found.

        :reset:      bool Quiesce the light when acquired.
        :exclusive:  bool Light is owned exclusively by process.
        """

        all_lights = []

        if cls._is_abstract():
            for subclass in cls.subclasses():
                all_lights.extend(subclass.all_lights(reset=reset, exclusive=exclusive))
            logger.info(f"{cls.__name__} found {len(all_lights)} lights total.")
        else:
            for light_info in cls.available_lights():
                try:
                    all_lights.append(cls(light_info, reset=reset, exclusive=exclusive))
                except LightUnavailable as error:
                    logger.error(f"{cls.__name__} {error}")
            logger.info(f"{cls.__name__} found {len(all_lights)} lights.")

        return all_lights

    @classmethod
    def first_light(cls, reset: bool = True, exclusive: bool = True) -> "Light":
        """Returns the first available light claimed by this class.

        :reset:      bool Quiesce the light when acquired.
        :exclusive:  bool Light is owned exclusively by process.

        Raises:
        busylight.lights.exceptions.NoLightsFound
        """

        if cls._is_abstract():
            for subclass in cls.subclasses():
                for light_info in subclass.available_lights():
                    try:
                        return subclass(light_info, reset=reset, exclusive=exclusive)
                    except LightUnavailable as error:
                        logger.error(f"{subclass.__name__} {error}")

        else:
            for light_info in cls.available_lights():
                try:
                    return cls(light_info, reset=reset, exclusive=exclusive)
                except LightUnavailable as error:
                    logger.error(f"{cls.__name__} {error}")
                    raise

        logger.info("No lights found.")
        raise NoLightsFound()

    @classmethod
    def _is_concrete(cls) -> bool:
        """This class implements support for a physical light."""
        return cls is not Light

    @classmethod
    def _is_abstract(cls) -> bool:
        """This class supports a family of physical lights."""
        return not cls._is_concrete()

    @staticmethod
    @abc.abstractmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        """A dictionary  of device identfiers support by this class.

        Keys are a tuple of integer vendor_id and product id, values
        are the marketing name associated with that device.
        """

    @staticmethod
    @abc.abstractmethod
    def vendor() -> str:
        """Device vendor name."""

    @classmethod
    @abc.abstractmethod
    def udev_rules(cls, mode: int = 0o0666) -> List[str]:
        """"""

        rules = []

        for subclass in cls.__subclasses__():
            rules.extend(subclass.udev_rules(mode=mode))
        return rules

    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:
        """
        :light_info: dict Describes hardware details of light.
        :reset:      bool Quiesce the light when acquired.
        :exclusive:  bool Light is owned exclusively by process.
        """
        try:
            if not self.claims(light_info):
                raise LightUnsupported(light_info)
        except KeyError:
            raise InvalidLightInfo(light_info)

        self.info = dict(light_info)
        for key, value in self.info.items():
            setattr(self, key, value)

        self._reset = reset
        self._exclusive = exclusive

        if exclusive:
            self.acquire()

        if reset:
            if exclusive:
                self.reset()
            else:
                self.acqurie()
                self.reset()
                self.release()

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(..., reset={self._reset}, exclusive={self._exclusive})"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: "Light") -> bool:
        return all(
            (
                self.vendor == other.vendor,
                self.vendor_id == other.vendor_id,
                self.product_id == other.product_id,
                self.name == other.name,
                self.path == other.path,
            )
        )

    def __lt__(self, other: "Light") -> bool:
        return any(
            (
                self.vendor < other.vendor,
                self.vendor_id < other.vendor_id,
                self.product_id < other.product_id,
                self.name < other.name,
                self.path < other.path,
            )
        )

    def reset(self) -> None:
        """Turn off the light and cancel any running async tasks."""
        self.off()
        self.cancel_tasks()

    @contextmanager
    def batch_update(self) -> Generator[None, None, None]:
        """Writes the software state to the device when the context manager exits."""

        yield

        if not self._exclusive:
            try:
                self.acquire()
            except Exception as error:
                logger.error("Failed to acquire {self!s} {self.path} {error}")
                return

        self.update()

        if not self._exclusive:
            try:
                self.release()
            except Exception as error:
                logger.error("Failed to release {self!s} {self.path} {error}")

    def on(self, color: Tuple[int, int, int]) -> None:
        """Activate the light with the supplied RGB color tuple."""

        with self.batch_update():
            self.color = color

    def off(self) -> None:
        """Turn the light off."""
        self.on((0, 0, 0))

    @property
    def name(self) -> str:
        """The product name for this device."""
        try:
            return self._name
        except AttributeError:
            pass
        self._name = self.supported_device_ids()[self.device_id]
        return self._name

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
        """True if the light does not respond to commands."""
        return not self.is_pluggedin

    @property
    def is_on(self) -> bool:
        """True if the software state of the light indicates the light is on."""
        return any(self.color)

    @property
    def is_off(self) -> bool:
        """True if the software state of the light indicates the light is off."""
        return not self.is_on

    @property
    def is_button(self) -> bool:
        """True if this device is a button."""
        return False

    @property
    def button_on(self) -> bool:
        """True if the button is the on state."""
        return False

    @property
    def read_strategy(self) -> Callable:
        """The read function used to communicate with the device."""
        return self.device.read

    @property
    def write_strategy(self) -> Callable:
        """The write function used to communicate with the device."""
        return self.device.write

    @property
    def red(self) -> int:
        """Red intensity value."""
        return getattr(self, "_red", 0)

    @red.setter
    def red(self, new_value: int) -> int:
        self._red = new_value

    @property
    def green(self) -> int:
        """Green intensity value."""
        return getattr(self, "_green", 0)

    @green.setter
    def green(self, new_value: int) -> int:
        self._green = new_value

    @property
    def blue(self) -> int:
        """Blue intensity value."""
        return getattr(self, "_blue", 0)

    @blue.setter
    def blue(self, new_value: int) -> int:
        self._blue = new_value

    @property
    def color(self) -> Tuple[int, int, int]:
        """A three channel color value in RGB order."""
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, new_value: Tuple[int, int, int]) -> None:
        try:
            self.red, self.green, self.blue = new_value
        except Exception as error:
            raise ValueError(f"unable to set color {new_value!r}: {error}") from None

    def update(self) -> None:
        """Write the software state to the device."""

        data = bytes(self)

        try:
            nbytes = self.write_strategy(data)
            logger.info(f"data:{len(data)} = {data!r} wrote {nbytes}")
        except Exception as error:
            logger.error(f"write_strategy raised {error} for {data}")
            raise LightUnavailable(self.path) from None

    @abc.abstractmethod
    def __bytes__(self) -> bytes:
        """Device software state in device format."""

    @property
    @abc.abstractmethod
    def device(self) -> Any:
        """Provides physical I/O to the device."""

    @abc.abstractmethod
    def acquire(self) -> None:
        """Acquire the device for use."""

    @abc.abstractmethod
    def release(self) -> None:
        """Release the device from use."""

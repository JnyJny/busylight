""" USB Connected Light
"""

import abc
import asyncio

from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Callable, Generator, Dict, List, Tuple, Type, TypeVar, Union

from loguru import logger

from .exceptions import (
    InvalidLightInfo,
    LightNotFound,
    LightUnavailable,
    LightUnsupported,
    NoLightsFound,
)

from .taskable import TaskableMixin

LightType = Type["Light"]

LightInfo = Dict[str, Union[bytes, int, str, Tuple[int, int]]]


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

        if cls._is_concrete():
            supported_lights.setdefault(cls.vendor(), cls.unique_device_names())

        for subclass in cls.subclasses():
            lights = supported_lights.setdefault(subclass.vendor(), [])
            lights.extend(subclass.unique_device_names())

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
        """Returns a list of all lights found in a stable ordering.

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

        return sorted(all_lights)

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
        are the marketing name associated with that device. Some tuples
        may identify devices with the same name.
        """

    @classmethod
    @lru_cache(maxsize=None)
    def unique_device_names(cls) -> List[str]:
        """A list of unique device names supported by this class."""

        if cls._is_concrete():
            return list(set(cls.supported_device_ids().values()))

        names = []
        for subclass in cls.subclasses():
            names.extend(subclass.unique_device_names())
        return names

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
        # for key, value in self.info.items():
        #    logger.debug("{self.__class__.__name__} adding {key} with {value}")
        #    setattr(self, key, value)

        self._reset = reset
        self._exclusive = exclusive

        if exclusive:
            self.acquire()

        if reset:
            self.reset()

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(..., reset={self._reset}, exclusive={self._exclusive})"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:

        if not isinstance(other, Light):
            return NotImplemented

        return all(
            [
                self.vendor() == other.vendor(),
                self.name == other.name,
                str(self.path) == str(other.path),
            ]
        )

    def __lt__(self, other: object) -> bool:

        if not isinstance(other, Light):
            return NotImplemented

        if self.vendor().lower() < other.vendor().lower():
            return True

        if not self.vendor().lower() == other.vendor().lower():
            return False

        if self.name.lower() < other.name.lower():
            return True

        if not self.name.lower() == other.name.lower():
            return False

        return str(self.path) < str(other.path)

    def reset(self) -> None:
        """Turn off the light and cancel any running async tasks."""

        self.off()
        self.cancel_tasks()

    @property
    def device_id(self) -> Tuple[int, int]:
        """A tuple of integer vendor and product identfiers."""
        try:
            return self._device_id
        except AttributeError:
            pass
        self._device_id: Tuple[int, int] = self.info["device_id"]
        return self._device_id

    @property
    def path(self) -> str:
        """An operating system specific filesystem path for this device."""
        try:
            return self._path
        except AttributeError:
            pass
        self._path: str = str(self.info["path"])
        return self._path

    @property
    def vendor_id(self) -> int:
        """An integer vendor identifier for this device."""
        try:
            return self._vendor_id
        except AttributeError:
            pass
        self._vendor_id: int = self.info["vendor_id"]
        return self._vendor_id

    @property
    def product_id(self) -> int:
        """An integer product identifier for this device."""
        try:
            return self._product_id
        except AttributeError:
            pass
        self._product_id: int = self.info["product_id"]
        return self._product_id

    @contextmanager
    def batch_update(self) -> Generator[None, None, None]:
        """Writes the software state to the device when the context manager exits."""
        yield
        self.update()

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
        self._name: str = self.supported_device_ids()[self.device_id]
        return self._name

    @property
    @abc.abstractmethod
    def is_pluggedin(self) -> bool:
        """True if the light is plugged in and responding to commands."""

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
    def red(self, new_value: int) -> None:
        self._red = new_value

    @property
    def green(self) -> int:
        """Green intensity value."""
        return getattr(self, "_green", 0)

    @green.setter
    def green(self, new_value: int) -> None:
        self._green = new_value

    @property
    def blue(self) -> int:
        """Blue intensity value."""
        return getattr(self, "_blue", 0)

    @blue.setter
    def blue(self, new_value: int) -> None:
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

    @contextmanager
    def exclusive_access(self) -> None:
        """If not in exclusive mode:
        - acquires the device for I/O
        - performs the I/O
        - releases the device
        """
        logger.info(f"Entering exclusive access for {self}")

        if not self._exclusive:
            logger.info(f"Acquiring device for {self}")
            self.acquire()
            logger.info(f"Acquired for {self}")

        yield

        if not self._exclusive:
            logger.info(f"Releasing device for {self}")
            self.release()
            logger.info(f"Released for {self}")
        logger.info(f"Exiting exclusive access for {self}")

    def update(self) -> None:
        """Write the software state to the device."""

        data = bytes(self)

        with self.exclusive_access():
            try:
                nbytes = self.write_strategy(data)
                logger.info(f"data:{len(data)} = {data!r} wrote {nbytes}")
            except Exception as error:
                logger.error(f"write_strategy raised {error} for {data!r}")
                raise LightUnavailable(f"{self} {self.path}") from None

        # if nbytes == -1:
        #    raise LightUnavailable(self.path)

    def matches(self, light_info: LightInfo) -> bool:
        """True if light_info matches info for this light instance."""

    @abc.abstractmethod
    def __bytes__(self) -> bytes:
        """Device software state in device format."""

    @property
    @abc.abstractmethod
    def device(self) -> Any:
        """Provides physical I/O to the device."""

    @abc.abstractmethod
    def acquire(self) -> None:
        """Acquire the device for use.

        Raises LightUnavailable if not able to acquire this device.
        """

    @abc.abstractmethod
    def release(self) -> None:
        """Release the device from use."""

"""Base class for USB connected lights.

While not intended to be instantiated directly, this class provides a
common interface for all USB connected lights and a mechanism for
discovering available lights on the system.

```python
from busylight_core import Light

all_lights = Light.all_lights()

for light in all_lights:
    light.on((255, 0, 0))  # Turn on the light with red color

for light in all_lights:
    light.off()  # Turn off all lights
````

"""

from __future__ import annotations

import abc
import contextlib
import platform
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

from functools import cache, cached_property

from loguru import logger

from .exceptions import (
    HardwareUnsupportedError,
    LightUnavailableError,
    NoLightsFoundError,
)
from .hardware import Hardware
from .mixins import TaskableMixin


class Light(abc.ABC, TaskableMixin):
    """Base class for USB connected lights.

    This base class provides a common interface for USB connected lights.

    Subclasses should inherit from this class, implement the abstract
    methods, and populate the `supported_device_ids` class variable
    with supported device IDs and their product names. The key for
    support_device_ids should be a tuple composed of the vendor ID and
    product ID, while the value should be the human-readable marketing
    name of the device.

    Note: If a subclass inherits from Light, but does not directly
          implement support for any specific hardware, it should leave
          the `supported_device_ids` class variable *empty*. This
          allows the base class to identify subclasses which do not
          support any specific hardware and act appropriately.

    Note: If the subclasses are not imported the package __init__, the
          abc.ABC.__subclasses__ machinery will not find them and your
          new lights will not be recognized.

    The Light class has been designed to be helpful for discovering
    and managing USB connected lights without having to know aprori
    details of the hardware present. In the vast majority of cases,
    you are not expected to create Light subclass instances directly
    and rely on these classmethods to discover and use lights.

    - Light.available_hardware() provides a list of recognized hardware.
    - Light.all_lights() returns all discovered lights ready for use.
    - Light.first_light() returns the first available light.

    If you know what devices you have connected and want to access
    them directly, you can use the Light subclasses directly using
    the same class methods.

    ```python
    from busylight_core.vendors.embrava import Blynclight
    from busylight_core.vendors.luxafor import Flag
    from busylight_core.vendors.thingm import Blink1

    blynclight = Blynclight.first_light()
    flag = Flag.first_light()
    all_blink1s = Blink1.all_lights()
    ```

    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {}

    @classmethod
    @cache
    def vendor(cls) -> str:
        """Get the vendor name for this device class.

        Returns a human-readable vendor name derived from the module structure.
        Device-specific subclasses should override this method to provide
        accurate vendor branding that matches the physical device labeling.

        :return: Title-cased vendor name for display in user interfaces
        """
        # EJO this is a low-effort way to get the vendor
        #     name from the module name. Subclasses can
        #     and should override this method to provide
        #     a more accurate vendor name.
        parts = cls.__module__.split(".")
        return parts[-2].title() if len(parts) >= 2 else "Unknown"

    @classmethod
    @cache
    def unique_device_names(cls) -> list[str]:
        """Get all unique marketing names for devices supported by this class.

        Returns the human-readable product names from the supported_device_ids
        mapping, with duplicates removed. Use this to display available device
        types to users or for device capability documentation.

        :return: Sorted list of unique device marketing names
        """
        return sorted(set(cls.supported_device_ids.values()))

    @classmethod
    @cache
    def unique_device_ids(cls) -> list[tuple[int, int]]:
        """Get all unique vendor/product ID pairs supported by this class.

        Returns the USB vendor and product ID combinations that this class
        can control. Use this for hardware enumeration, udev rule generation,
        or debugging device detection issues.

        :return: Sorted list of (vendor_id, product_id) tuples
        """
        return sorted(set(cls.supported_device_ids.keys()))

    @classmethod
    def claims(cls, hardware: Hardware) -> bool:
        """Check if this class can control the given hardware device.

        Determines whether this Light subclass supports the specific hardware
        by checking if the device's vendor/product ID pair matches any entry
        in the supported_device_ids mapping. Use this during device discovery
        to find the appropriate Light subclass for each detected device.

        :param hardware: Hardware instance to test for compatibility
        :return: True if this class can control the hardware device
        """
        return hardware.device_id in cls.supported_device_ids

    @classmethod
    @cache
    def subclasses(cls) -> list[type[Self]]:
        """Return a list of all subclasses of this class."""
        subclasses = []

        if cls != Light and cls.supported_device_ids:
            subclasses.append(cls)

        for subclass in cls.__subclasses__():
            subclasses.extend(subclass.subclasses())

        return sorted(subclasses, key=lambda s: s.__module__)

    @classmethod
    @cache
    def supported_lights(cls) -> dict[str, list[str]]:
        """Return a dictionary of supported lights by vendor.

        Keys are vendor names, values are a list of product names.
        """
        supported_lights: dict[str, list[str]] = {}

        for subclass in cls.subclasses():
            names = supported_lights.setdefault(subclass.vendor(), [])
            names.extend(subclass.unique_device_names())

        return supported_lights

    @classmethod
    def available_hardware(cls) -> dict[type[Self], list[Hardware]]:
        """Discover all compatible hardware devices available for control.

        Scans the system for USB devices that match known vendor/product ID
        combinations and groups them by the Light subclass that can control
        them. Use this for device discovery, inventory management, or when
        you need to present users with available device options.

        The returned Hardware instances represent devices that were found
        and claimed by Light subclasses, but may still be in use by other
        processes. Actual device acquisition occurs during Light initialization.

        :return: Mapping from Light subclass to list of compatible Hardware instances
        """
        available_lights: dict[type[Self], list[Hardware]] = {}

        for hardware in Hardware.enumerate():
            if cls.supported_device_ids:
                if cls.claims(hardware):
                    logger.debug(f"{cls.__name__} claims {hardware}")
                    claimed = available_lights.setdefault(cls, [])
                    claimed.append(hardware)
            else:
                for subclass in cls.subclasses():
                    if subclass.claims(hardware):
                        logger.debug(f"{subclass.__name__} claims {hardware}")
                        claimed = available_lights.setdefault(subclass, [])
                        claimed.append(hardware)

        return available_lights

    @classmethod
    def all_lights(
        cls,
        *,
        reset: bool = True,
        exclusive: bool = True,
        predicate: Callable[[Hardware], bool] | None = None,
    ) -> list[Self]:
        """Create initialized Light instances for all available compatible devices.

        Discovers all compatible hardware and returns Light instances ready for
        immediate use. Each light is initialized with the specified configuration
        and can be used to control its device without further setup.

        Use this when you want to control all connected lights simultaneously,
        such as for synchronized effects or system-wide status indication.

        :param reset: Reset devices to known state during initialization
        :param exclusive: Acquire exclusive access to prevent interference
        :param predicate: Optional callable to filter devices based on custom criteria
        :return: List of initialized Light instances, empty if none found
        """
        lights: list[Self] = []

        for subclass, devices in cls.available_hardware().items():
            for device in devices:
                if predicate and not predicate(device):
                    logger.info(f"Hardware {device} did not satisfy predicate")
                    continue
                try:
                    lights.append(subclass(device, reset=reset, exclusive=exclusive))
                except Exception as error:
                    logger.info(f"Failed to acquire {device}: {error}")

        return lights

    @classmethod
    def first_light(
        cls,
        *,
        reset: bool = True,
        exclusive: bool = True,
        predicate: Callable[[Hardware], bool] | None = None,
    ) -> Self:
        """Create the first available Light instance ready for immediate use.

        Discovers compatible devices and returns the first successfully
        initialized Light instance. Use this when you need a single light
        for simple status indication and don't care about the specific
        device type or vendor.

        :param reset: Reset device to known state during initialization
        :param exclusive: Acquire exclusive access to prevent interference
        :param predicate: Optional callable to filter devices based on custom criteria
        :return: Initialized Light instance ready for control
        :raises NoLightsFoundError: If no compatible devices found or init fails
        """
        for subclass, devices in cls.available_hardware().items():
            for device in devices:
                if predicate and not predicate(device):
                    logger.info(f"Hardware {device} did not satisfy predicate")
                    continue
                try:
                    return subclass(device, reset=reset, exclusive=exclusive)
                except Exception as error:
                    logger.info(f"Failed to acquire {device}: {error}")
                    raise

        raise NoLightsFoundError(cls)

    @classmethod
    def at_path(cls, path: str, reset: bool = True, exclusive: bool = True) -> Self:
        """Create a Light instance for the device at the specified path.

        :param path: Filesystem path to the target hardware device
        :param reset: Reset the device to a known state during initialization
        :param exclusive: Acquire exclusive access to prevent interference
        :return: Initialized Light instance for the specified device

        :raises NoLightsFoundError: If no device found with a matching path
        """
        path = path.encode("utf-8")
        return cls.first_light(
            reset=reset,
            exclusive=exclusive,
            predicate=lambda hardware: hardware.path == path,
        )

    @classmethod
    def udev_rules(cls, mode: int = 0o666) -> dict[tuple[int, int], list[str]]:
        """Return a dictionary of udev rules for the light subclass.

        The keys of the dictionary are device ID tuples, while the
        values are lists of udev rules for a particular light.  If
        duplicate device IDs are encountered, the first device ID
        wins and subsequent device IDs are ignored.

        :param mode: int - file permissions for the device, defaults to 0o666
        """
        rules = {}

        rule_formats = [
            'SUBSYSTEMS=="usb", ATTRS{{idVendor}}=="{vid:04x}", ATTRS{{idProduct}}=="{pid:04x}", MODE="{mode:04o}"',  # noqa: E501
            'KERNEL=="hidraw*", ATTRS{{idVendor}}=="{vid:04x}", ATTRS{{idProduct}}=="{pid:04x}", MODE="{mode:04o}"',  # noqa: E501
        ]

        if cls.supported_device_ids:
            for vid, pid in cls.unique_device_ids():
                content = rules.setdefault((vid, pid), [])
                content.append(f"# {cls.vendor()} {cls.__name__} udev rules")
                for rule_format in rule_formats:
                    content.append(rule_format.format(vid=vid, pid=pid, mode=mode))
        else:
            for subclass in cls.subclasses():
                subclass_rules = subclass.udev_rules(mode=mode)
                for key, value in subclass_rules.items():
                    if key not in rules:
                        rules[key] = value

        return rules

    def __init__(
        self,
        hardware: Hardware,
        *,
        reset: bool = False,
        exclusive: bool = True,
    ) -> None:
        """Initialize a Light instance with the specified hardware device.

        Creates a Light instance bound to the given hardware device and
        configures it for use. The hardware should be obtained from
        Hardware.enumerate() and verified with the class's claims() method.

        Use this constructor when you have specific hardware and want to
        create a Light instance for direct device control.

        :param hardware: Hardware instance representing the device to control
        :param reset: Reset the device to a known state during initialization
        :param exclusive: Acquire exclusive access to prevent interference
        :raises HardwareUnsupportedError: If Light class cannot control hardware
        """
        if not self.__class__.claims(hardware):
            raise HardwareUnsupportedError(hardware, self.__class__)

        self.hardware = hardware
        self._reset = reset
        self._exclusive = exclusive

        if exclusive:
            self.hardware.acquire()

        if reset:
            self.reset()

    def __repr__(self) -> str:
        repr_fmt = "{n}({h!r}, *, reset={r}, exclusive={e}"
        return repr_fmt.format(
            n=self.__class__.__name__,
            h=self.hardware,
            r=self._reset,
            e=self._exclusive,
        )

    def __str__(self) -> str:
        """Return a human-readable string representation of the light."""
        return f"{self.vendor()} {self.name}@{self.path}"

    @cached_property
    def path(self) -> str:
        """The path to the hardware device."""
        return self.hardware.path.decode("utf-8")

    @cached_property
    def platform(self) -> str:
        """The discovered operating system platform name."""
        system = platform.system()
        match system:
            case "Windows":
                return f"{system}_{platform.release()}"
            case _:
                return system

    @property
    def exclusive(self) -> bool:
        """Return True if the light has exclusive access to the hardware."""
        return self._exclusive

    @property
    def was_reset(self) -> bool:
        """Return True if the light was reset when the hardware was initialized."""
        return self._reset

    @cached_property
    def sort_key(self) -> tuple[str, str, str]:
        """Return a tuple used for sorting lights.

        The tuple consists of:
        - vendor name in lowercase
        - device name in lowercase
        - hardware path
        """
        return (self.vendor().lower(), self.name.lower(), self.path)

    def __eq__(self, other: object) -> bool:
        try:
            return self.sort_key == other.sort_key
        except AttributeError:
            raise TypeError from None

    def __lt__(self, other: Light) -> bool:
        if not isinstance(other, Light):
            return NotImplemented

        for self_value, other_value in zip(self.sort_key, other.sort_key, strict=False):
            if self_value != other_value:
                return self_value < other_value

        return False

    def __hash__(self) -> int:
        """Return a hash value for the light based on its sort key."""
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self.sort_key)
            return self._hash

    @cached_property
    def name(self) -> str:
        """The human-readable marketing name of this light."""
        return self.supported_device_ids[self.hardware.device_id]

    @property
    def hex(self) -> str:
        """The hexadecimal representation of the light's state."""
        return bytes(self).hex(":")

    @property
    def read_strategy(self) -> Callable[[int, int | None], bytes]:
        """The read method used by this light."""
        return self.hardware.handle.read

    @property
    def write_strategy(self) -> Callable[[bytes], None]:
        """The write method used by this light."""
        return self.hardware.handle.write

    def release(self) -> None:
        """Release the light's exclusive access to the hardware.

        If the light was acquired in exclusive mode, this method releases
        the hardware resource, allowing other processes to access it.
        If the light was not acquired in exclusive mode, no action is taken.
        """
        if self._exclusive:
            logger.debug(f"Releasing exclusive access to {self.name}")
            self.hardware.release()
            self._exclusive = False

    @contextlib.contextmanager
    def exclusive_access(self) -> Generator[None, None, None]:
        """Manage exclusive access to the light.

        If the device is not acquired in exclusive mode, it will be
        acquired and released automatically.

        No actions are taken if the light is already acquired
        in exclusive mode.
        """
        if not self._exclusive:
            self.hardware.acquire()

        yield

        if not self._exclusive:
            self.hardware.release()

    def update(self) -> None:
        """Send the current light state to the physical device.

        Serializes the light's current state and transmits it to the hardware
        device using the appropriate platform-specific protocol. Call this
        method after making changes to light properties to apply them to
        the physical device.

        The method handles platform-specific protocol differences automatically,
        such as adding leading zero bytes on Windows 10.

        :raises LightUnavailableError: If device communication fails
        """
        state = bytes(self)

        match self.platform:
            case "Windows_10":
                state = bytes([0]) + state
            case "Darwin" | "Linux" | "Windows_11":
                pass
            case _:
                logger.info(f"Unsupported OS {self.platform}, hoping for the best.")

        with self.exclusive_access():
            logger.debug(f"{self.name} payload {state.hex(':')}")
            try:
                self.write_strategy(state)
            except Exception as error:
                logger.error(f"{self}: {error}")
                raise LightUnavailableError(self) from None

    @contextlib.contextmanager
    def batch_update(self) -> Generator[None, None, None]:
        """Defer device updates until multiple properties are changed.

        Context manager that accumulates multiple property changes and sends
        them to the device in a single update operation when exiting the
        context. Use this when changing multiple light properties (color,
        brightness, effects) to reduce USB communication overhead and improve
        performance.

        :return: Context manager for batching multiple property updates
        """
        yield
        self.update()

    def on(
        self,
        color: tuple[int, int, int],
        led: int = 0,
        interrupt: bool = True,
    ) -> None:
        """Activate the light with the specified RGB color.

        Cancels any pre-existing animation tasks before setting the color,
        then dispatches to the vendor-specific _on() implementation.

        :param color: RGB intensity values from 0-255 for each color component
        :param led: Target LED index, 0 affects all LEDs on the device
        :param interrupt: If True, cancel any existing tasks before activating the light
        """
        if interrupt:
            self.cancel_tasks()
        self._on(color, led)

    @abc.abstractmethod
    def _on(
        self,
        color: tuple[int, int, int],
        led: int = 0,
    ) -> None:
        """Vendor implementation of light activation.

        Subclasses implement this to set the hardware to the given color.
        Task cancellation is handled by on() before this method is called.

        :param color: RGB intensity values from 0-255 for each color component
        :param led: Target LED index, 0 affects all LEDs on the device
        """
        raise NotImplementedError

    def off(self, led: int = 0) -> None:
        """Turn off the light by setting it to black.

        Deactivates the specified LED(s) by setting their color to black (0, 0, 0).
        Use this to turn off status indication while keeping the device available
        for future color changes.

        For multi-LED devices, specify the LED index or use 0 to turn off all LEDs.
        Single-LED devices ignore the led parameter.

        :param led: Target LED index, 0 affects all LEDs on the device
        """
        self.on((0, 0, 0), led)

    def reset(self) -> None:
        """Turn the light off and cancel associated asynchronous tasks."""
        self.off()

    @abc.abstractmethod
    def __bytes__(self) -> bytes:
        """Return the light's state suitable for writing to the device."""
        raise NotImplementedError

    @property
    def nleds(self) -> int:
        """The number of individually addressable LEDs in the light.

        A value of zero indicates that the light does not have
        individually addressable LEDs.
        """
        return 0

    @property
    @abc.abstractmethod
    def color(self) -> tuple[int, int, int]:
        """Get the current RGB color of the light."""
        raise NotImplementedError

    @color.setter
    @abc.abstractmethod
    def color(self, value: tuple[int, int, int]) -> None:
        """Set the RGB color of the light.

        Updates the light's color state to the specified RGB values.
        Device-specific implementations should store this value and
        apply it during the next update() call.

        :param value: RGB intensity values from 0-255 for each color component
        """
        raise NotImplementedError

    @property
    def is_lit(self) -> bool:
        """Check if the light is currently lit."""
        return any(self.color)

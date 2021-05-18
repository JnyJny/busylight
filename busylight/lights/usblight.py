"""Abstract Base Class for USB Lights
"""

import abc
import hid  # type: ignore

from contextlib import contextmanager
from threading import RLock
from typing import (
    Any,
    Callable,
    cast,
    Dict,
    Iterator,
    List,
    Tuple,
    Type,
    Union,
)

from .exceptions import USBLightNotFound
from .exceptions import USBLightUnknownVendor
from .exceptions import USBLightUnknownProduct
from .exceptions import USBLightInUse
from .exceptions import USBLightIOError

from .thread import CancellableThread


class USBLight(abc.ABC):
    """A generic USB light that uses HIDAPI to control devices.

    This abstract base class attempts to support as many different
    lights as possible using the same interface. Light capabilities vary
    widely, but all lights support the following operations:

    - on with a color
    - off
    - blink off and on with a color

    Concrete implementations may expose more capabilities than required
    by USBLight, however it is up to the user to discover them.

    Concrete implementations of USBLight will provide:

    Abstract Properties
    - VENDOR_IDS : List[int]
    - PRODUCT_IDS : List[int]
    - vendor : str

    Abstract Methods
    - __bytes__
    - on
    - blink
    - reset

    In addition to providing USB infrastructre to subclasses, USBLight
    provides several classmethods:
    - supported_lights : list of subclasses
    - vendor_ids : list of integer vendor identifiers
    - first_light : returns the first available light
    - all_lights : returns all available lights

    The `first_light` and `all_lights` classmethods have different
    behaviors depending on the invoking class. If the methods are
    called by a subclass of USBLight, the method only returns lights
    supported by the subclass. If invoked via `USBlight`, returned
    available lights will be of all supported subclasses.
    """

    @classmethod
    def supported_lights(cls) -> List[Type["USBLight"]]:
        """Returns a list of USBLight subclasses supporting specific lights."""

        return cls.__subclasses__()

    @classmethod
    def vendor_ids(cls) -> List[int]:
        """Returns a list of supported integer vendor identifiers."""

        if cls.__name__ == "USBLight":
            vendor_ids: List[List[int]] = []
            for subclass in cls.supported_lights():
                vendor_ids.append(subclass.vendor_ids())
            return sum(vendor_ids, [])

        return cls.VENDOR_IDS  # type: ignore

    @classmethod
    def first_light(cls) -> "USBLight":
        """Returns the first supported and unused USB light found.

        If a suitable light is not found, USBLightNotFound is
        raised. This method can be called from USBLight or any of it's
        subclasses. If called from a subclass, only lights supported
        by the subclass are returned.

        :return: configured USBLight subclass instance.

        Raises:
        - USBLightNotFound
        """

        if cls.__name__ != "USBLight":

            for vendor_id in cls.vendor_ids():
                for light_entry in hid.enumerate(vendor_id):
                    try:
                        return cls.from_dict(light_entry)
                    except (
                        USBLightUnknownVendor,
                        USBLightUnknownProduct,
                        USBLightInUse,
                    ):
                        pass
            else:
                raise USBLightNotFound()

        for supported_light in cls.supported_lights():
            try:
                return supported_light.first_light()
            except USBLightNotFound:
                pass
        else:
            raise USBLightNotFound()

    @classmethod
    def all_lights(cls) -> List["USBLight"]:
        """Returns a list of configured lights.

        If called by a subclass of USBLight, the list will
        consist of initialized lights supported by the subclass.

        eg.
        >>> lights = FooLight.all_lights()
        >>> all(isinstance(light, FooLight) for light in lights)
        True

        If called by USBLight, the list will consist of
        initialized lights supported by all subclasses.

        >>> lights = USBLight.all_lights()
        >>> all(isinstance(light, FooLight) for light in lights)
        False

        If the list is empty, no supported lights were found or
        all the lights are currently in use.

        :return: List[object]
        """

        lights = []
        if cls.__name__ != "USBLight":

            while True:
                try:
                    lights.append(cls.first_light())
                except USBLightNotFound:
                    break
            return lights

        for supported_light in cls.supported_lights():
            lights.extend(supported_light.all_lights())
        return lights

    @classmethod
    def from_dict(cls, info: Dict[str, Union[int, str, bytes]]):
        """Returns a USBLight subclass instance configured using a dictionary.

        In most cases, the info dictionary is constructed by a
        call to `hid.enumerate`. The dictionary must contain keys
        for 'vendor_id', 'product_id' and 'path' at a bare minimum.
        If one or more of these keys are missing, KeyError is raised.

        :param info: Dict[str, Union[int, str, bytes]]
        :return: configured USBLight subclass instance.

        Raises:
        - USBLightUnknownVendor
        - USBLightUnknownProduct
        - USBLightInUse
        - KeyError
        """

        return cls(
            cast(int, info["vendor_id"]),
            cast(int, info["product_id"]),
            cast(bytes, info["path"]),
        )

    def __init__(
        self, vendor_id: int, product_id: int, path: bytes, reset: bool = False
    ) -> None:
        """Configure and acquire a USBLight instance

        Given the vendor_id, product_id and path for a USB device,
        configure and acquire the device. The device can be optionally
        "reset" to a known state or left in it's current (unknown)
        state.

        :param vendor_id: int 16-bit value
        :param product_id: int 16-bit value
        :param path: bytes
        :param reset: bool

        Raises:
        - USBLightUnknownVendor
        - USBLightUnknownProduct
        - USBLightInUse
        """
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.path = path
        self.acquire(reset=reset)

    def __del__(self):
        """Release the light before reclaiming this object."""
        self.release()

    def __repr__(self):
        return "{}(vendor_id=0x{:04x}, product_id=0x{:04x}, path={}, ...)".format(
            type(self).__name__, self.vendor_id, self.product_id, self.path
        )

    def __str__(self):
        return f"{self.name}: {self.identifier}"

    @property
    def device(self) -> hid.device:
        """HID API handle used to perform IO on USB devices.

        The device is not ready for use until the `acquire`
        method is called.
        """
        try:
            return self._device
        except AttributeError:
            pass
        self._device: hid.device = hid.device()
        return self._device

    @property
    def strategy(self) -> Callable:
        """The write function used to communicate with the device.

        The default write strategy is `hid.device.write`, however
        some devices may require `hid.device.send_feature_report`
        instead.

        The strategy function is expected to take `bytes` as it's
        sole argument and return the number of bytes written. A
        return value of -1 indicates error.
        """
        return self.device.write

    @property
    def vendor_id(self) -> int:
        """16-bit USB vendor identifier.

        Setting vendor_id with a value not supported by this
        class will raise USBLightUnknownVendor.
        """
        return getattr(self, "_vendor_id", None)

    @vendor_id.setter
    def vendor_id(self, value: int) -> None:
        if value not in self.VENDOR_IDS:
            raise USBLightUnknownVendor(hex(value))
        self._vendor_id = value

    @property
    def product_id(self) -> int:
        """16-bit USB product identifier.

        Setting product_id with a value not supported by this
        class will raise USBLightUnknownProduct.
        """
        return getattr(self, "_product_id", None)

    @product_id.setter
    def product_id(self, value: int) -> None:
        if self.PRODUCT_IDS and value not in self.PRODUCT_IDS:
            raise USBLightUnknownProduct(hex(value))
        self._product_id = value

    @property
    def info(self) -> Dict[str, Union[int, str, bytes]]:
        """USB Human Interface Device dictionary for this device.

        Raises:
        - USBLightIOError if unable to find matching dictionary.
          The light may have been unplugged.
        """
        try:
            return self._info
        except AttributeError:
            pass

        for info in hid.enumerate(self.vendor_id, self.product_id):
            if info["path"] == self.path:
                self._info: Dict[str, Union[int, str, bytes]] = dict(info)
                break
        else:
            raise USBLightIOError(f"Device information missing: {self.path!s}")

        return self._info

    @property
    def name(self) -> str:
        """String concatenation of vendor and title-cased product_string."""
        try:
            return self._name
        except AttributeError:
            pass
        product = str(self.info.get("product_string", "unknown product name"))
        self._name: str = f"{self.vendor} {product.title()}"
        return self._name

    @property
    def identifier(self) -> str:
        """String concatenation of hexadecimal vendor and product identifiers."""
        return f"0x{self.vendor_id:04x}:0x{self.product_id:04x}"

    @property
    def lock(self) -> RLock:
        """A threading.RLock used to serialize access to the USB device.

        The lock is used to serialize access to the device property and
        when updating the in-memory representation of the hardware
        state.  This is only important when multiple threads are
        attempting to access the these resources at the same time. In
        practice, concrete implementations of USBLight are not expected
        to need direct access to lock.

        See `acquire`, `update`, `batch_update` and `release` for usage.
        """
        try:
            return self._lock
        except AttributeError:
            pass
        self._lock: RLock = RLock()
        return self._lock

    @property
    def animation_thread(self) -> Union[CancellableThread, None]:
        """A busylight.lights.thread.CancellableThread animating this light.

        The animation thread runs a generator function that takes this
        light as an argument and calls yield at frequent intervals. If
        animation_thread is None, the light is not being animated.
        """
        return getattr(self, "_animation_thread", None)

    @property
    def color(self) -> Tuple[int, int, int]:
        """A 3-tuple of integers representing red, green and blue color intensities."""
        return getattr(self, "_color", (0, 0, 0))

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self._color = tuple(values)

    @property
    def is_acquired(self) -> bool:
        """Is the light hardware acquired?

        If True, this light has been sucessfully opened and is ready for use.
        """
        return bool(getattr(self, "_device", False))

    @property
    def is_animating(self) -> bool:
        """Is this light currently being animated?"""
        return self.animation_thread is not None

    @property
    def is_on(self) -> bool:
        """Is the light currently on?"""
        return any(self.color)

    @contextmanager
    def batch_update(self) -> Iterator[None]:
        """Context manager useful for grouping updates to a device.

        Manipulations to the light's in-memory representation of the

        hardware state are serialized on entry to the context manager
        and the hardware state is flushed to the hardware on exit.

        Raises:
        - USBLightIOError
        """
        with self.lock:
            yield
            self.update()

    def acquire(self, reset: bool) -> None:
        """Open a HID USB light for writing.

        This method opens the device for I/O and optionally
        triggers a device reset to a known state. Concrete
        implementations provide a `reset` method.

        :param reset: bool

        Raises:
        - USBLightInUse
        - USBLightIOError
        """
        with self.lock:
            try:
                self.device.open_path(self.path)
            except IOError:
                raise USBLightInUse(
                    self.vendor_id, self.product_id, self.path
                ) from None
            except Exception as error:
                raise USBLightIOError(f"error opening {self.path!s}: {error}") from None

            if reset:
                self.reset()
                self.update()

    def release(self) -> None:
        """Shutdown the animation thread and close the device.

        Releasing the light will cancel any active animation threads and
        call `hid.device.close`. The light must be re-acquired with the
        `acquire` method if the caller wishes to continue using this
        instance.
        """

        with self.lock:
            self.stop_animation()
            try:
                self.device.close()
            except:
                pass
            del self._device

    def start_animation(self, animation: Callable) -> None:
        """Start an animation thread running the given `animation`.

        See busylight.lights.thread.CancellableThread for more details.

        :param animation: Callable

        Raises:
        - USBLightIOError
        """
        if not self.is_acquired:
            raise USBLightIOError(f"light is not acquired: {self.identifier}")

        self.stop_animation()

        self._animation_thread = CancellableThread(
            animation(self), f"animation-{self.identifier}"
        )
        self._animation_thread.start()

    def stop_animation(self) -> None:
        """Cancel the animation thread (if running).

        Call this method from the main thread to stop the animation thread.
        """
        try:
            self._animation_thread.cancel()
            del self._animation_thread
        except:
            pass

    def update(self):
        """Updates the hardware with the current software state.

        Raises:
        - USBLightIOError
          The light may have been unplugged.
          The light may have been released.
        """

        data = bytes(self)

        try:
            with self.lock:
                nbytes = self.strategy(data)
        except ValueError as error:
            raise USBLightIOError(str(error)) from None

        if nbytes != len(data):
            raise USBLightIOError(f"write returned {nbytes}")

    @property
    @abc.abstractmethod
    def VENDOR_IDS(self) -> List[int]:
        """List of two-byte vendor identifiers supported by this class."""

    @property
    @abc.abstractmethod
    def PRODUCT_IDS(self) -> List[int]:
        """List of two-byte product identifiers supported by this class.

        An empty list indicates all products from this vendor are supported.
        """

    @property
    @abc.abstractmethod
    def vendor(self) -> str:
        """Vendor name supported by this class."""

    @abc.abstractmethod
    def __bytes__(self):
        """The hardware control data to write to the USB device."""

    @abc.abstractmethod
    def on(self, color: Tuple[int, int, int]) -> None:
        """Turn the light on with the specified color.

        :param color: Tuple[int, int, int]
        """
        self.color = color

    def off(self) -> None:
        """Turns the light off."""
        self.on((0, 0, 0))

    @abc.abstractmethod
    def blink(
        self,
        color: Tuple[int, int, int],
        speed: int = 1,
    ) -> None:
        """Light blinks on and off with the specified color and speed.

        When queried, the light is "on" with the specified color even
        though it is blinking.  Speed should be an integer in the
        range of 0 thru 2 inclusive:

        - 1 : slow
        - 2 : medium
        - 3 : fast

        :param color: Tuple[int, int, int]
        :param speed: int

        Raises:
        - ValueError for speed out of range.

        """
        self.color = color
        if speed not in [1, 2, 3]:
            raise ValueError(f"Speed is out of range: {speed}")

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset the light to it's initial configuration.

        Only effects the in-memory representation of the hardware
        state. The physical light is not changed until a call to the
        `update` method.
        """

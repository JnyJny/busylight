"""Abstract Base Class for USB Lights
"""

import abc
import hid

from contextlib import contextmanager, suppress
from typing import Any, Dict, Generator, List, Tuple, Union

from .exceptions import USBLightNotFound
from .exceptions import USBLightUnknownVendor
from .exceptions import USBLightUnknownProduct
from .exceptions import USBLightInUse
from .exceptions import USBLightIOError

from ..thread import AnimationThread


class USBLight(abc.ABC):
    """A generic USB light that uses HIDAPI to control devices.

    This abstract base class attempts to support as many different
    lights as possible using the same interface. Light capabilities vary
    widely, but all lights support the following operations:

    - on with a color
    - off
    - blink on and off with a color (some lights need help)

    Concrete implementations may expose more capabilities than required
    by USBLight, however it is up to the user to discover them.

    Concrete implementations of USBLight will need to provide:

    Abstract Properties
    - VENDOR_IDS : List[int]
    - PRODUCT_IDS : List[int]
    - vendor : str
    - state : Any (not really)
    - color : Tuple[int, int, int]
    - is_on : bool

    Abstract Methods
    - on
    - off
    - blink
    - reset

    While the `state` abstract property is typed with Any, in reality it
    is expected to be some sort of byte buffer (like a bitvector ;).  If
    this is not the case, the concrete implementation should override
    the `USBLight.update` method to take whatever actions are appropriate
    to operate their specific hardware.
    """

    @classmethod
    def supported_lights(cls) -> List[object]:
        """Returns a list of classes supporting specific lights."""

        return cls.__subclasses__()

    @classmethod
    def first_light(cls):
        """Returns the first supported and unused USB light found.

        If a suitable light is not found, USBLightNotFound is
        raised.

        :return: configured USBLight subclass instance.

        Raises:
        - USBLightNotFound
        """

        ignored_exceptions = [
            USBLightUnknownVendor,
            USBLightUnknownProduct,
            USBLightInUse,
        ]

        for vendor_id in cls.VENDOR_IDS:
            for light_entry in hid.enumerate(vendor_id):
                with suppress(ignored_exceptions):
                    return cls.from_dict(light_entry)
        else:
            raise USBLightNotFound()

    @classmethod
    def from_dict(cls, info: Dict[str, Union[int, str]]):
        """Returns a configured USBLight subclass using a dictionary.

        In most cases, the info dictionary is constructed by a
        call to hid.enumerate.

        :param info: Dict[str, Union[int, str]]
        :return: configured USBLight subclass instance.

        Raises:
        - USBLightUnknownVendor
        - USBLightUnknownProduct
        - USBLightInUse
        """

        return cls(info["vendor_id"], info["product_id"], info["path"])

    def __init__(
        self, vendor_id: int, product_id: int, path: bytes, reset: bool = False
    ) -> None:
        """Given the vendor_id, product_id and path for a USB device,
        configure and acquire the device.

        :param vendor_id: int 16-bit value
        :param product_id: int 16-bit value
        :param path: bytes

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
        return "{}(vendor_id=0x{:04x}, product_id=0x{:04x}, path={})".format(
            self.__class__.__name__, self.vendor_id, self.product_id, self.path
        )

    def __str__(self):
        return f"{self.name}: {self.identifier}"

    @property
    def device(self) -> hid.device:
        """HID API handle used to perform IO on USB devices."""
        try:
            return self._device
        except AttributeError:
            pass
        self._device = hid.device()
        return self._device

    @property
    def vendor_id(self) -> int:
        """16-bit USB vendor identifier."""
        return getattr(self, "_vendor_id", None)

    @vendor_id.setter
    def vendor_id(self, value: int) -> None:
        if value not in self.VENDOR_IDS:
            raise USBLightUnknownVendor(value)
        self._vendor_id = value

    @property
    def product_id(self) -> int:
        """16-bit USB product identifier."""
        return getattr(self, "_product_id", None)

    @product_id.setter
    def product_id(self, value: int) -> None:
        if self.PRODUCT_IDS and value not in self.PRODUCT_IDS:
            raise USBLightUnknownProduct(value)
        self._product_id = value

    @property
    def info(self) -> Dict[str, Union[int, str]]:
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
                self._info = dict(info)
                break
        else:
            raise USBLightIOError("Device information missing")

        return self._info

    @property
    def name(self) -> str:
        """Concatenation of vendor and title-cased product_string."""
        try:
            return self._name
        except AttributeError:
            pass
        self._name = f"{self.vendor} {self.info['product_string'].title()}"
        return self._name

    @property
    def identifier(self) -> str:
        """Concatenation of hex vendor and product identifiers."""
        return f"0x{self.vendor_id:04x}:0x{self.product_id:04x}"

    @property
    def animation_thread(self) -> Union[AnimationThread, None]:
        """"A busylight.thread.CancellableThread animating this light."""
        return getattr(self, "_animation_thread", None)

    @property
    def color(self) -> Tuple[int, int, int]:
        """A 3-tuple of integers representing red, green and blue."""
        return getattr(self, "_color", (0, 0, 0))

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self._color = tuple(values)

    @property
    def is_acquired(self) -> bool:
        """Is the light hardware acquired?"""
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
    def batch_update(self) -> None:
        """Context manager to group updates to a device.

        Raises: - USBLightIOError
        """
        yield
        self.update()

    def acquire(self, reset: bool) -> None:
        """Open a HID USB light for writing.

        This method opens the device for I/O and optionally
        resets the device with a known state.

        :param reset: bool

        Raises:
        - USBLightInUse
        - USBLightIOError
        """
        try:
            self.device.open_path(self.path)
        except IOError:
            raise USBLightInUse(self.vendor_id, self.product_id, self.path) from None
        except Exception as error:
            raise USBLightIOError(f"error opening {self.path}: {error}") from None

        if reset:
            self.reset()
            self.update()

    def release(self) -> None:
        """Shutdown the animation thread and close the device."""

        self.stop_animation()
        try:
            self.device.close()
        except:
            pass
        del self._device

    def start_animation(self, animation: Generator) -> None:
        """Start an animation thread running the given `animation`.

        See busylight.thread.CancellableThread for more details.

        :param animation: Generator
        """
        # EJO what happens if we start an animation on a released light?
        self.stop_animation()
        self._animation_thread = AnimationThread(animation(self), self.identifier)
        self._animation_thread.start()

    def stop_animation(self) -> None:
        """Cancel the animation thread (if running)."""
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

        buf = bytes(self.state)
        try:
            nbytes = self.device.write(buf)
        except ValueError as error:
            raise USBLightIOError(str(error)) from None

        if nbytes != len(buf):
            raise USBLightIOError(f"write returned {nbytes}") from None

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

    @property
    @abc.abstractmethod
    def state(self) -> Any:
        """Internal light state with a bytes representation."""

    @abc.abstractmethod
    def on(self, color: Tuple[int, int, int]) -> None:
        """Turn the light on with the specified color.

        :param color: Tuple[int, int, int]
        """

    @abc.abstractmethod
    def off(self) -> None:
        """Turns the light off."""

    @abc.abstractmethod
    def blink(
        self,
        color: Tuple[int, int, int],
        speed: int = 0,
    ) -> None:
        """Light blinks on and off with the specified color.

        :param color: Tuple[int, int, int]
        :param speed: int
        """

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset the light to it's initial configuration.

        Only effects the in-memory representation of the hardware
        state. The physical light is not effected until a call to the
        update method.
        """

"""Abstract Base Class for USB Lights
"""

import abc
import hid


from typing import Any, Dict, Generator, List, Tuple, Union

from contextlib import contextmanager, suppress

from .exceptions import USBLightNotFound
from .exceptions import USBLightUnknownVendor
from .exceptions import USBLightUnknownProduct
from .exceptions import USBLightInUse
from .exceptions import USBLightIOError

from ..thread import CancellableThread


class USBLight(metaclass=abc.ABCMeta):
    """A generic USB light that uses HIDAPI to control devices."""

    @classmethod
    def first_light(cls):
        """Returns the first unused USB light found.

        :return: configured USBLight subclass instance.

        Raises:
        - USBLightNotFound
        """

        for vendor_id in cls.VENDOR_IDS:
            for light_entry in hid.enumerate(vendor_id):
                try:
                    return cls.from_dict(light_entry)
                except (USBLightUnknownVendor, USBLightUnknownProduct, USBLightInUse):
                    pass
        else:
            raise USBLightNotFound()

    @classmethod
    def from_dict(cls, info: Dict[str, Union[int, str]]):
        """Returns a configured USBLight subclass located via the supplied dictionary.

        :param info: Dict[str, Union[int, str]]

        Raises:
        - USBLightUnknownVendor
        """

        return cls(info["vendor_id"], info["product_id"], info["path"])

    def __init__(
        self, vendor_id: int, product_id: int, path: bytes, reset: bool = True
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
        return getattr(self, "_vendor_id", None)

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
        """
        try:
            return self._info
        except AttributeError:
            pass
        for info in hid.enumerate(self.vendor_id, self.product_id):
            if info["path"] == self.path:
                self._info = dict(info)
                return self._info
        else:
            raise USBLightIOError("Device information missing")

    @property
    def name(self) -> str:
        """Concatenation of vendor and title-cased product_string."""
        try:
            return self._name
        except AttributeError:
            pass
        self._name = f"{self.__vendor__} {self.info['product_string'].title()}"
        return self._name

    @property
    def identifier(self) -> str:
        """Concatenation of hex vendor and product identifiers."""
        return f"0x{self.vendor_id:04x}:0x{self.product_id:04x}"

    @property
    def animation_thread(self) -> Union[CancellableThread, None]:
        """"A busylight.thread.CancellableThread animating this light."""
        return getattr(self, "_animation_thread", None)

    @property
    def animating(self) -> bool:
        """Is this light currently being animated?"""
        return self.animation_thread is not None

    @contextmanager
    def batch_update(self) -> None:
        """Context manager that flushes changes to the device when the manager exits."""
        yield
        self.update()

    def stop_animation(self) -> None:
        """Cancel the animation thread (if running)."""
        try:
            self._animation_thread.cancel()
            del self._animation_thread
        except AttributeError:
            pass

    def start_animation(self, animation: Generator) -> None:
        """Start an animation thread running the given `animation`.

        :param animation: Generator
        """

        self.stop_animation()
        self._animation_thread = CancellableThread(
            animation, f"animation-{self.identifier}"
        )
        self._animation_thread.start()

    def release(self) -> None:
        """Shutdown animation thread and close the device."""
        self.stop_animation()
        self.device.close()
        del self._device

    def acquire(self, reset: bool = False) -> None:
        """Open a HID USB light for writing.

        :param reset: bool
        """
        try:
            self.device.open_path(self.path)
        except IOError:
            raise USBLightInUse(self.vendor_id, self.product_id, self.path) from None

        if reset:
            self.state.reset()
            self.update()

    def update(self):
        """Updates the hardware with the current software state."""

        buf = bytes(self.state)
        nbytes = self.device.write(buf)
        if nbytes != len(buf):
            raise USBLightIOError()

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
    def __vendor__(self) -> str:
        """Vendor name supported by this class."""

    @property
    @abc.abstractmethod
    def __family__(self) -> str:
        """Family name of devices supported by this class."""

    @property
    @abc.abstractmethod
    def state(self) -> Any:
        """Internal light state."""

    @property
    @abc.abstractmethod
    def color(self) -> Tuple[int, int, int]:
        """A 3-tuple of 16-bit integers representing red, green and blue."""
        pass

    @color.setter
    @abc.abstractmethod
    def color(self, values: Tuple[int, int, int]) -> None:
        pass

    @property
    @abc.abstractmethod
    def is_on(self) -> bool:
        """Is the light on right now?"""

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

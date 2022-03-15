"""Abstract USB Light

Find and control supported USB connected presense lights.


Developer Notes:
================

Adding support for a new light requires:

- Optionally create a new vendor directory: `busylight/lights/<vendor>`
- Update `busylight/lights/<vendor>/__init__.py` to export
  the new USBLight subclass
- Create `busylight/lights/<vendor>/<device_name>.py`
  - Define a USBLight subclass
  - Implement all USBLight abstract methods
  - By convention, I've kept the implementation specific details in
    a file named `busylight/lights/<vendor>/<device>_impl.py`
- Update `busylight/lights/__init__.py` to import the new light subclass
  and add it to the `__all__` list.

If the new light is a subclass of an existing subclass, consult
the files for the Embrava Blynclight and the Plantronics Status
Indicator for an example of how to handle that situation.

Consider using the BitVector-for-human library if the new light's
control packet has sub-byte bit fields. See
busylight.lights.embrava.blynclight for an example.

Some devices have byte-aligned control fields which makes a
BitVector-approach overly complex: see
busylight.lights.luxafor.flag for an example of building the
control packet in the __bytes__ method.

"""


import abc
import asyncio

from contextlib import contextmanager
from typing import Awaitable, Callable, Generator, Dict, List, Optional, Tuple, Union

import hid

from loguru import logger

from .exceptions import (
    InvalidHidInfo,
    LightNotFound,
    LightUnavailable,
    LightUnsupported,
    NoLightsFound,
)

from .speed import Speed
from .color import ColorTuple
from .effects import FrameGenerator, FrameTuple

HidInfo = Dict[str, Union[bytes, int, str]]


class USBLight(abc.ABC):
    """Communicate with a generic USB attached light using HID API.

    The USBLight class can be used to discover and control supported
    USB-attached presense lights without having to know device
    specific information.

    >> red = (255, 0, 0)
    >> green = (0, 255, 0)
    >> light = USBLight.first_light()
    >> light.on(red)
    >> light.blink(green)
    >> light.off()

    The USBLight provides discoverability via class methods:
    - USBLight.subclasses()
    - USBLight.supported_lights()
    - USBLight.available()
    - USBLight.claims()
    - USBLight.udev_rules()

    Available lights can be acquired using class methods:
    - USBLight.first_light()
    - USBLight.all_lights()

    All USBLight subclasses also individually support the classmethods:

    >> from busylight.lights import Blynclight
    >> blynclights = Blynclight.all_lights()
    >> Blynclight.supported()
    [<class 'busylight.lights.embrava.blynclight.Blynclight'>,
     <class 'busylight.lights.plantronics.status_indicator.Status_Indicator'>]

    The capabilities of USB lights from different vendors vary
    greatly, however all of them support the ability to turn on with a
    color and turn off. Most also have to the ability to blink on and
    off with a specified duty cycle (BlinkStick devices need software
    intervention to blink).

    More involved effects can be achieved via software; writing
    new color values at the desired frequency using the async method
    `apply_effect` and a `FrameGenerator`.
    """

    @classmethod
    def available(cls) -> List[HidInfo]:
        """Returns a list of recognized USB light devices currently
        discoverable (plugged-in but may be in use). Returns an empty
        list if no devices are discovered.

        :return: List[Dict[str, Union[byte, int, str]]]
        """
        return [hidinfo for hidinfo in hid.enumerate() if cls.claims(hidinfo)]

    @classmethod
    def supported_lights(cls) -> Dict[str, List[str]]:
        """Returns a dictionary whose keys are USBLight vendor names and values
        are device marketing names supported for that vendor.
        """
        supported_lights = {}

        if cls is USBLight:
            for subclass in cls.subclasses():
                results = subclass.supported_lights()
                for vendor, names in results.items():
                    supported_lights.setdefault(vendor, []).extend(names)
            return supported_lights

        values = sorted(set(cls.SUPPORTED_DEVICE_IDS.values()))
        supported_lights.setdefault(cls.vendor, []).extend(values)
        return supported_lights

    @classmethod
    def subclasses(cls) -> List["USBLight"]:
        """Returns a list of USBLight subclasses supporting different products."""
        subclasses = []
        if cls is USBLight:
            for subclass in cls.__subclasses__():
                subclasses.extend(subclass.subclasses())
            return subclasses

        subclasses.append(cls)
        subclasses.extend(cls.__subclasses__())
        return subclasses

    @classmethod
    def claims(cls, hidinfo: HidInfo) -> bool:
        """Returns True if this class claims the device described by `hidinfo`.

        Raises:
        - InvalidHidInfo
        """
        if cls is USBLight:
            for subclass in cls.subclasses():
                if subclass.claims(hidinfo):
                    logger.debug(f"{subclass.__name__} claims {hidinfo=}")
                    return True
            return False

        logger.debug(f"{hidinfo=}")
        try:
            device_id = (hidinfo["vendor_id"], hidinfo["product_id"])
        except KeyError as error:
            logger.debug("missing keys from hidinfo {hidinfo=}")
            raise InvalidHidInfo(hidinfo) from None

        return device_id in cls.SUPPORTED_DEVICE_IDS

    @classmethod
    def all_lights(cls, reset: bool = True) -> List["USBLight"]:
        """Returns a list of USBLight-subclass instances ready for use.

        If no lights are discovered, an empty list is returned.
        :reset: bool
        :returns: list[USBLight]
        """
        all_lights = []

        if cls is USBLight:
            for subclass in cls.subclasses():
                all_lights.extend(subclass.all_lights(reset=reset))
            logger.debug(f"{cls.__name__} found {len(all_lights)} lights total")
            return sorted(all_lights)

        for device in cls.available():
            try:
                all_lights.append(cls.from_dict(device, reset=reset))
            except LightUnavailable as error:
                logger.debug(f"{cls.__name__} {error}")
            logger.debug(f"{cls.__name__} found {len(all_lights)} lights")
        return all_lights

    @classmethod
    def first_light(cls, reset: bool = True) -> "USBLight":
        """Returns the first available light opened and ready for use.

        :reset: bool
        :return: USBLight
        Raises:
        - NoLightsFound
        """
        if cls is USBLight:
            for subclass in cls.subclasses():
                try:
                    return subclass.first_light(reset=reset)
                except NoLightsFound as error:
                    logger.debug(f"{subclass.__name__}.firstlight() -> {error}")
            raise NoLightsFound()

        for device in cls.available():
            try:
                return cls.from_dict(device, reset=reset)
            except LightUnavailable as error:
                logger.debug(f"{cls.__name__}.from_dict() {error}")
                raise

        raise NoLightsFound()

    @classmethod
    def udev_rules(cls, mode: int = 0o0666) -> List[str]:
        """Returns a list of Linux udev subsystem rules for all supported lights.

        :mode: int
        :return: list[str]
        """
        rules = []

        if cls is USBLight:
            for subclass in cls.subclasses():
                rules.extend(subclass.udev_rules())
            return rules

        rule_formats = [
            'KERNEL=="hidraw*", ATTRS{{idVendor}}=="{vid:04x}", ATTRS{{idProduct}}=="{pid:04x}", MODE="{mode:04o}"',
            'SUBSYSTEM=="usb", ATTRS{{idVendor}}=="{vid:04x}", ATTRS{{idProduct}}=="{pid:04x}", MODE="{mode:04o}"',
        ]

        rules.append(
            f"# Rules for {cls.vendor} Family of Devices: {len(cls.SUPPORTED_DEVICE_IDS)}"
        )
        for n, ((vid, pid), name) in enumerate(cls.SUPPORTED_DEVICE_IDS.items()):
            logger.debug(f"udev rule for {vid:04x}, {pid:04x} {name}")
            rules.append(f"# {n} {cls.vendor} {name}")
            for rule_format in rule_formats:
                rules.append(rule_format.format(vid=vid, pid=pid, mode=mode))

        return rules

    @classmethod
    def from_dict(cls, hidinfo: HidInfo, reset: bool = True) -> "USBLight":
        """Instantiate a new light instance from the contents of `info` dictionary.

        :hidinfo: dict[str, Union[bytes, int, str]]
        :reset: bool
        :return: USBLight

        Raises:
        - InvalidHidInfo if the supplied HidInfo dictionary has missing keys.
        - LightUnsupported if the device described by HidInfo is not supported.
        - LightUnavailable if the device cannot be accessed.
        """

        if cls is USBLight:
            for subclass in cls.subclasses():
                if subclass.claims(hidinfo):
                    return subclass(hidinfo, reset)
            raise LightUnsupported.from_dict(hidinfo)

        return cls(hidinfo, reset)

    def __init__(
        self,
        hidinfo: HidInfo,
        reset: bool = True,
    ) -> None:
        """
        :hidinfo: HidInfo
        :reset: bool

        Raises:
        - LightUnsupported
        - LightUnavailable
        """

        self._hidinfo = hidinfo

        if (
            self.vendor_id,
            self.product_id,
        ) not in self.SUPPORTED_DEVICE_IDS:
            raise LightUnsupported.from_dict(hidinfo)

        self.acquire()

        if reset:
            self.reset()

    @property
    @abc.abstractmethod
    def SUPPORTED_DEVICE_IDS(self) -> Dict[Tuple[int, int], str]:
        """Dictionary of device identifiers supported by this class.

        Keys are a 2-tuple of vendor_id and product_id and values
        are strings, typically the device's marketing name.
        """

    @property
    @abc.abstractmethod
    def vendor(self) -> str:
        """Device vendor name."""

    @abc.abstractmethod
    def __bytes__(self) -> bytes:
        """The hardware control data written to the device."""

    @abc.abstractmethod
    def on(self, color: ColorTuple) -> Optional[Awaitable[None]]:
        """Activate the light with the specified color.

        The light may optionally return an Awaitable instance
        that implements additional software support the light
        needs for this operation.

        :color: 3-tuple of 8-bit RGB values
        :return: Awaitable or None
        """
        self.color = color

    @abc.abstractmethod
    def off(self) -> None:
        """Turn the light off."""

    @abc.abstractmethod
    def blink(
        self, color: ColorTuple, blink: Speed = Speed.Slow
    ) -> Optional[Awaitable[None]]:
        """Turn the light on and off with the given color and speed.

        The light may optionally return an Awaitable instance
        that implements additional software support the light
        needs for this operation.

        Raises:
        - NotImplementedError - device doesn't support hardware blinking
        """

    async def apply_effect(self, effect: FrameGenerator) -> None:
        """Apply the given `effect` FrameGenerator instance to this light.

        The update loop runs for as long as the FrameGenerator supplies
        FrameTuples.

        :effect: FrameGenerator
        """
        logger.debug(f"{self.name} {effect=}")
        for color, interval in effect():
            logger.debug(f"{self.name} {color} {interval}")
            self.on(color)
            await asyncio.sleep(interval)
        logger.debug(f"{self.name} exiting from apply_effect")

    def __repr__(self) -> str:
        vendor = f"vendor_id=0x{self.vendor_id:04x}"
        product = f"product_id=0x{self.product_id:04x}"
        path = f"path={self.path!r}"
        return f"{self.__class__.__name__}({vendor}, {product}, {path})"

    def __str__(self) -> str:
        return self.name

    def __del__(self) -> None:
        self.release()

    def __eq__(self, other) -> bool:

        return all(
            (
                self.vendor == other.vendor,
                self.vendor_id == other.vendor_id,
                self.product_id == other.product_id,
                self.name == other.name,
                self.path == other.path,
            )
        )

    def __lt__(self, other) -> bool:

        return any(
            (
                self.vendor < other.vendor,
                self.vendor_id < other.vendor_id,
                self.product_id < other.product_id,
                self.name < other.name,
                self.path < other.path,
            )
        )

    @property
    def hidinfo(self) -> HidInfo:
        return getattr(self, "_hidinfo", {})

    @property
    def vendor_id(self) -> int:
        return self._hidinfo["vendor_id"]

    @property
    def product_id(self) -> int:
        return self._hidinfo["product_id"]

    @property
    def path(self) -> str:
        return self._hidinfo["path"].decode("utf-8")

    @property
    def product_string(self) -> str:
        return self._hidinfo.get("product_string", "")

    @property
    def serial_number(self) -> str:
        return self._hidinfo.get("serial_number", "")

    @property
    def release_number(self) -> int:
        return self._hidinfo.get("release_number", 0)

    @property
    def manufacturer_string(self) -> str:
        return self._hidinfo.get("manufacturer_string", "")

    @property
    def usage_page(self) -> int:
        return self._hidinfo.get("usage_page", 0)

    @property
    def usage(self) -> int:
        return self._hidinfo.get("usage", 0)

    @property
    def name(self) -> str:
        """Device product name (read-only)."""
        try:
            return self._name
        except AttributeError:
            pass
        self._name = f"{self.vendor} {self.product_string.title()}"
        return self._name

    @property
    def device(self) -> hid.device:
        """HID API handle used to perform IO to this USB device."""
        try:
            return self._device
        except AttributeError:
            pass
        self._device = hid.device(self.vendor_id, self.product_id)
        return self._device

    @property
    def write_strategy(self) -> Callable[[bytes], int]:
        """The write function used to communicate with the device.

        The default write strategy is `hid.device.write`, however
        some devices may require `hid.device.send_feature_report`
        instead.

        The write_strategy function is expected to take `bytes` as it's
        sole argument and return the number of bytes written. A
        return value of -1 indicates error.
        """
        return self.device.write

    @property
    def read_strategy(self) -> Callable[[int], bytes]:
        """The read function used to communicate with the device.

        The default read strategy is `hid.device.read`, however some
        devices may require `hid.device.read_feature_report` instead.

        The read_strategy function is expected to take `nbytes` as
        it's sole argument and returns a `bytes` instance of the
        data read.
        """
        return self.device.read

    @property
    def is_pluggedin(self) -> bool:
        # XXX needs work
        try:
            results = self.device.read_strategy(8)
            logger.debug(f"light pluggedin {self!r} {results=!r}")
            return True
        except OSError as error:
            logger.debug(f"light unplugged {self!r} {error}")
        return False

    @property
    def is_unplugged(self) -> bool:
        return not self.is_pluggedin

    @property
    def red(self) -> int:
        """Red intensity value [0-255]."""
        return getattr(self, "_red", 0)

    @red.setter
    def red(self, new_red: int) -> None:
        self._red = max(min(new_red, 0xFF), 0)

    @property
    def green(self) -> int:
        """Green intensity value [0-255]."""
        return getattr(self, "_green", 0)

    @green.setter
    def green(self, new_green: int) -> None:
        self._green = max(min(new_green, 0xFF), 0)

    @property
    def blue(self) -> int:
        """Blue intensity value [0-255]."""
        return getattr(self, "_blue", 0)

    @blue.setter
    def blue(self, new_blue: int) -> None:
        self._blue = max(min(new_blue, 0xFF), 0)

    @property
    def color(self) -> ColorTuple:
        """Tuple of integer red, green and blue intensity values."""
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, new_color: ColorTuple) -> None:
        self.red, self.green, self.blue = new_color

    def reset(self, off_color: ColorTuple = (0, 0, 0)) -> None:
        """Set the light to an initial quiesced state."""
        self.on(off_color)

    def acquire(self) -> None:
        """Acquire the light's resources.

        Raises:
        - LightUnavailable if hid.device.open_path fails.
        - InvalidHidInfo if self.hidinfo is missing the `path` key.
        """

        try:
            self.device.open_path(self.hidinfo["path"])
        except KeyError as error:
            logger.debug("{error} {self.hidinfo=}")
            raise InvalidHidInfo(self.hidinfo) from None
        except OSError as error:
            logger.debug(f" {error}")
            raise LightUnavailable.from_dict(self.hidinfo) from None

    def release(self) -> None:
        """Release this light's resources.

        After a light has been released, it needs to be re-acquired using
        the `acquire` method.
        """
        logger.debug(f"releasing id={id(self):x}")
        try:
            if self._device:
                self.device.close()
                del self._device
        except AttributeError:
            logger.debug(f"_device attribute not yet instantiated")

    def update(self) -> None:
        """Send the light's in-memory state, bytes(self), to the device.

        Calls the `write_strategy` property with the `bytes` representation of
        the light.

        Raises:
        - LightUnavailable
        """
        data = bytes(self)

        try:
            nbytes = self.write_strategy(data)
        except ValueError as error:
            logger.debug(f"write_strategy raised {error}")
            raise LightUnavailable.from_dict(self.hidinfo) from None

        msg = (
            f"{self.name} @ {self.path} {data.hex(':')} {self.write_strategy}={nbytes}"
        )

        if nbytes < 0:
            logger.error(msg)
            # EJO In general, unplugging the device is the most likely
            #     cause of write_strategy returning < 0. Also possible
            #     there are operating system permission issues
            #     blocking access to the device, but there isn't
            #     enough information from "< 0" to be able to
            #     differentiate between the two failure modes.
            raise LightUnavailable(self.vendor_id, self.product_id, self.path)

        logger.debug(msg)

    @contextmanager
    def batch_update(self) -> Generator[None, None, None]:
        """Context manager which updates hardware state when it exits."""
        # EJO Considering operating the lights in an unacquired mode
        #     where acquire is called right before update and then the
        #     light is released directly afterwards. lights that
        #     return an async coroutine for animating the update
        #     effect are a problem.
        #
        #     This might help solve a problem with windows where
        #     exclusive-open of devices isn't a thing. more thinking
        #     required.
        yield
        # self.acquire()
        self.update()
        # self.release()

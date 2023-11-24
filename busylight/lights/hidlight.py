"""USB Human Interface Device (HID) Light Support
"""

from typing import Any, Dict, List, Union

import hid

from loguru import logger

from .hid import enumerate as hid_enumerate
from .hid import Device as hid_device
from .light import Light, LightInfo

from .exceptions import LightUnavailable


class HIDLight(Light):
    """USB Human Interface Device (HID) Light Support

    I/O to the device is conducted thru interfaces provided by the
    hidapi package.

    HID is a simplified method of interacting with USB devices like
    keyboards, mice and joysticks.

    The HIDLight class provides methods for managing the hid.device
    instance and discovering known connected HID devices that were
    abstract in the Light superclass.
    """

    @classmethod
    def _is_physical(cls) -> bool:
        return cls is not HIDLight

    @classmethod
    def available_lights(cls) -> List[LightInfo]:

        available = []
        for hidinfo in hid_enumerate():
            try:
                hidinfo["device_id"] = (hidinfo["vendor_id"], hidinfo["product_id"])
            except KeyError as error:
                logger.error(f"broken HID info {hidinfo}: {error}")
                continue

            if not cls.claims(hidinfo):
                continue

            info = dict(hidinfo)
            available.append(info)

        logger.info(f"{cls.__name__} found {len(available)}")
        return available

    @classmethod
    def udev_rules(cls, mode: int = 0o0666) -> List[str]:

        rules = []

        if cls._is_abstract():
            for subclass in cls.subclasses():
                rules.extend(subclass.udev_rules(mode=mode))
            return rules

        rule_formats = [
            'KERNEL=="hidraw*", ATTRS{{idVendor}}=="{vid:04x}", ATTRS{{idProduct}}=="{pid:04x}", MODE="{mode:04o}"',
            'SUBSYSTEM=="usb", ATTRS{{idVendor}}=="{vid:04x}", ATTRS{{idProduct}}=="{pid:04x}", MODE="{mode:04o}"',
        ]

        devices = cls.supported_device_ids()
        rules.append(f"# Rules for {cls.vendor()} Family of Devices: {len(devices)}")
        for n, ((vid, pid), name) in enumerate(devices.items(), start=1):
            logger.info(f"udev rule for {vid:04x}, {pid:04x} {name}")
            rules.append(f"# {n} {cls.vendor()} {name}")
            for rule_format in rule_formats:
                rules.append(rule_format.format(vid=vid, pid=pid, mode=mode))

        return rules

    @property
    def device(self):
        """A busylight.lights.hid.Device instance configured for use
        with this device.

        The device is not open until the acquire method has been
        called successfully.
        """
        try:
            return self._device
        except AttributeError:
            pass
        self._device: hid_device = hid_device()
        return self._device

    @property
    def is_pluggedin(self) -> bool:

        try:
            results = self.read_strategy(8, timeout_ms=100)
            return True
        except (ValueError, OSError):
            pass
        return False

    def acquire(self) -> None:

        try:
            self.device.open_path(self.info["path"])
            logger.info(f"{self} open_path({self.path}) succeeded")
        except OSError as error:
            logger.error(f"open_path failed: {error}")
            raise LightUnavailable(self.path) from None

    def release(self) -> None:

        self.device.close()
        logger.info(f"{self} close succeeded")

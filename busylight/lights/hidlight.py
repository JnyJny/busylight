""" USB Human Interface Device (HID) Light Support
"""

from typing import Any, Callable, Dict, List, Union

import hid

from loguru import logger

from .light import Light, LightInfo

from .exceptions import LightUnavailable


class HIDLight(Light):
    """A USB connected device implementing a light, indicator lamp or button.

    I/O to the device is thru interfaces provided by the hidapi package.
    """

    @classmethod
    def _is_concrete(cls) -> bool:
        return cls is not HIDLight

    @classmethod
    def available_lights(cls) -> List[LightInfo]:

        available = []
        for hidinfo in hid.enumerate():
            try:
                hidinfo["device_id"] = (hidinfo["vendor_id"], hidinfo["product_id"])
            except KeyError as error:
                logger.error(f"broken HID info {hidinfo}: {error}")
                continue

            if not cls.claims(hidinfo):
                continue

            info = dict(hidinfo)
            available.append(info)

        logger.info(f"{cls} found {len(available)}")
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
        rules.append(f"# Rules for {cls.vendor} Family of Devices: {len(devices)}")
        for n, ((vid, pid), name) in enumerate(devices.items()):
            logger.info(f"udev rule for {vid:04x}, {pid:04x} {name}")
            rules.append(f"# {n} {cls.vendor} {name}")
            for rule_format in rule_formats:
                rules.append(rule_format.format(vid=vid, pid=pid, mode=mode))

        return rules

    @property
    def device(self) -> hid.device:
        try:
            return self._device
        except AttributeError:
            pass
        self._device: hid.device = hid.device(*self.device_id)
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

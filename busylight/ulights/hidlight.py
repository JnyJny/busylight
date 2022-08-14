"""
"""

from typing import Any, Callable, Dict, List, Union

import hid

from loguru import logger

from .light import Light, LightInfo


class HIDLight(Light):
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

    @property
    def device(self) -> hid.device:
        try:
            return self._device
        except AttributeError:
            pass
        self._device = hid.device(*self.device_id)
        return self._device

    @property
    def is_pluggedin(self) -> bool:

        try:
            self.device.error()
            return True
        except ValueError:
            pass
        return False

    def acquire(self) -> None:

        try:
            self.device.open_path(self.path)
            logger.info(f"{self.name} open_path({self.path}) succeeded")
        except OSError as error:
            logger.error(f"open_path failed: {error}")
            raise LightUnavailable(self.path) from None

    def release(self) -> None:

        self.device.close()

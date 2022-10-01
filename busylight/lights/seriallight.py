""" USB Serial Light Support
"""


from typing import Callable, List

from loguru import logger

from serial import Serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo
from serial.serialutil import SerialException

from .light import Light, LightInfo
from .exceptions import LightUnavailable


class _UnrecognizedDevice(Exception):
    pass


class SerialLight(Light):
    """A USB connected device implementing a light, indicator lamp or button.

    I/O to the device is thru interfaces provided by the pyserial package.
    """

    @classmethod
    def _is_concrete(cls) -> bool:
        return cls is not SerialLight

    @staticmethod
    def _make_lightinfo(device: ListPortInfo) -> LightInfo:
        """Convert a serial.tools.list_ports_common.ListPortInfo
        to a LightInfo dictionary.

        The format of this dictionary is loosely based on the
        dictionary produced by `hid.enumerate`.

        Note: Not all of the HID fields are discoverable with the
              serial interface.
        """

        if not device.vid and not device.pid:
            raise _UnrecognizedDevice(device)

        return {
            "vendor_id": device.vid,
            "product_id": device.pid,
            "device_id": (device.vid, device.pid),
            "serial_number": device.serial_number,
            "product_string": device.description,
            "manufacturer_string": device.manufacturer,
            "path": device.device,
        }

    @classmethod
    def available_lights(cls) -> List[LightInfo]:

        available_lights = []

        for device in list_ports.comports():
            try:
                light_info = cls._make_lightinfo(device)
            except _UnrecognizedDevice:
                continue

            if cls.claims(light_info):
                available_lights.append(light_info)

        logger.info(f"{cls} found {len(available_lights)}")

        return available_lights

    @classmethod
    def udev_rules(cls, mode: int = 0o0666) -> List[str]:
        # EJO do serial USB devices need udev rules on Linux? I think so yes.
        return []

    @property
    def device(self) -> Serial:
        try:
            return self._device
        except AttributeError:
            pass

        self._device: Serial = Serial(timeout=1)
        self._device.port = self.path

        return self._device

    @property
    def is_pluggedin(self) -> bool:

        if not self.device.isOpen():
            return False

        try:
            self.device.timeout = 1
            return True
        except SerialException:
            pass
        return False

    def acquire(self) -> None:

        try:
            self.device.open()
            logger.info(f"{self} open() succeeded")
        except Exception as error:
            logger.debug("open failed for {self.path}: {error}")
            raise LightUnavailable(self.path) from None

    def release(self) -> None:

        self.device.close()
        logger.info(f"{self} close succeeded")

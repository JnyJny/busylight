""" USB Serial Light
"""


from typing import Callable, List

from loguru import logger

from serial import Serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from .light import Light, LightInfo


class UnrecognizedDevice(Exception):
    pass


class SerialLight(Light):
    """ """

    @classmethod
    def _is_concrete(cls) -> bool:
        return cls is not SerialLight

    @staticmethod
    def _make_lightinfo(device: ListPortInfo) -> LightInfo:
        """Convert a serial.tools.list_ports_common.ListPortInfo
        to a LightInfo dictionary.
        """

        if not device.vid and not device.pid:
            raise UnrecognizedDevice(device)

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
            except UnrecognizedDevice:
                continue

            if cls.claims(light_info):
                available_lights.append(light_info)

        logger.info(f"{cls} found {len(available_lights)}")

        return available_lights

    @property
    def device(self) -> Serial:
        try:
            return self._device
        except AttributeError:
            pass

        self._device = Serial(self.path)

        return self._device

    @property
    def read_strategy(self) -> Callable:
        return self.device.read

    @property
    def write_strategy(self) -> Callable:
        return self.device.write

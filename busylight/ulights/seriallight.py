""" USB Serial Light
"""


from typing import Any


from loguru import logger
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from .light import Light, LightInfo


class UnrecognizedDevice(Exception):
    pass


class SerialLight(Light):
    """ """

    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not SerialLight

    @staticmethod
    def _make_lightinfo(device: ListPortInfo) -> LightInfo:
        """Convert a serial.tools.list_ports_common.ListPortInfo
        to a dictionary.
        """

        if not device.vid and not device.pid:
            raise UnrecognizedDevice(device)

        return {
            "vendor_id": device.vid,
            "product_id": device.pid,
            "serial_number": device.serial_number,
            "product_string": device.description,
            "manufacturer_string": device.manufacturer,
            "path": device.device,
        }

    @classmethod
    def available_lights(cls) -> list[LightInfo]:

        available_lights = []

        for device in list_ports.comports():
            try:
                light_info = cls._make_lightinfo(device)
            except UnrecognizedDevice:
                continue

            if cls.claims(light_info):
                available_lights.append(light_info)

        logger.debug(f"{cls} found {len(available_lights)}")

        return available_lights

    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:
        """ """
        logger.debug(f"{light_info}")

        self.info = dict(light_info)
        for key, value in self.info.items():
            setattr(self, key, value)

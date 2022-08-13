""" USB Serial Light
"""


from typing import Any


from loguru import logger
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from .light import Light, LightInfo

SerialInfo = dict[Any, Any]


class NotUSBDevice(Exception):
    pass


class SerialLight(Light):
    """ """

    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not SerialLight

    @staticmethod
    def make_lightinfo(device: ListPortInfo) -> LightInfo:

        if not device.vid and not device.pid:
            raise NotUSBDevice(device)

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
                light_info = cls.make_lightinfo(device)
            except NotUSBDevice:
                continue

            if cls.claims(light_info):
                available_lights.append(light_info)
        logger.debug(f"{cls} found {len(available_lights)}")

        return available_lights

    @classmethod
    def from_info(cls, info: LightInfo) -> "SerialLight":
        raise NotImplementedError("from_info")

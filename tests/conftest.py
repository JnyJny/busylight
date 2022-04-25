"""
"""

from contextlib import suppress
from random import choice
from typing import Dict, Generator, List, Union
from unittest import mock
from unittest.mock import Mock, PropertyMock

import pytest

from busylight.lights import USBLight
from busylight.manager import LightManager

from loguru import logger

from . import device_hidinfo


def synthetic_lights_for_subclass(
    subclass: type(USBLight),
) -> Generator[USBLight, None, None]:
    """Creates a USBLight with mocked `device` property for each (vid,pid)
    defined by subclass.

    """
    for hidinfo in device_hidinfo(subclass):
        with mock.patch("hid.device"):
            light = subclass.from_dict(hidinfo, reset=False)
            del light._device
        light._device = Mock(name="hid.device")
        light._device.write.return_value = 1
        light._device.send_feature_report.return_value = 1
        light._device.open_path.return_value = None
        light._device.read.return_value = []
        light._device.get_feature_report.return_value = []

        yield light


@pytest.fixture()
def hidinfo_list() -> Generator[List[Dict[str, Union[bytes, int, str]]], None, None]:
    """List of real light dictionaries."""
    hidinfos = [
        {
            "path": b"DevSrvsID:4295116793",
            "vendor_id": 10168,
            "product_id": 493,
            "serial_number": "3e57c10d",
            "release_number": 257,
            "manufacturer_string": "ThingM",
            "product_string": "blink(1) mk3",
            "usage_page": 65451,
            "usage": 8192,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116918",
            "vendor_id": 1240,
            "product_id": 62322,
            "serial_number": "",
            "release_number": 256,
            "manufacturer_string": "GREYNUT LTD",
            "product_string": "LUXAFOR ORB",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116722",
            "vendor_id": 1240,
            "product_id": 63560,
            "serial_number": "",
            "release_number": 2,
            "manufacturer_string": "BLL Company ApS",
            "product_string": "BLL Lamp",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116777",
            "vendor_id": 10171,
            "product_id": 15309,
            "serial_number": "",
            "release_number": 256,
            "manufacturer_string": "PLENOM APS",
            "product_string": "BUSYLIGHT",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116896",
            "vendor_id": 8352,
            "product_id": 16869,
            "serial_number": "BS032974-3.0",
            "release_number": 512,
            "manufacturer_string": "Agile Innovative Ltd",
            "product_string": "BlinkStick",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116700",
            "vendor_id": 11277,
            "product_id": 1,
            "serial_number": "",
            "release_number": 256,
            "manufacturer_string": "",
            "product_string": "Blynclight",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116761",
            "vendor_id": 11277,
            "product_id": 10,
            "serial_number": "",
            "release_number": 1,
            "manufacturer_string": "",
            "product_string": "Blynclight Mini",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116874",
            "vendor_id": 1151,
            "product_id": 53253,
            "serial_number": "",
            "release_number": 1,
            "manufacturer_string": "",
            "product_string": "Plantronics Status Indicator",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116829",
            "vendor_id": 1240,
            "product_id": 62322,
            "serial_number": "",
            "release_number": 256,
            "manufacturer_string": "Microchip Technology Inc.",
            "product_string": "LUXAFOR FLAG",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116814",
            "vendor_id": 1240,
            "product_id": 62322,
            "serial_number": "",
            "release_number": 256,
            "manufacturer_string": "GREYNUT LTD",
            "product_string": "LUXAFOR MUTE",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
        {
            "path": b"DevSrvsID:4295116744",
            "vendor_id": 11277,
            "product_id": 16,
            "serial_number": "",
            "release_number": 256,
            "manufacturer_string": "",
            "product_string": "Blynclight Plus",
            "usage_page": 65280,
            "usage": 1,
            "interface_number": 0,
        },
    ]

    yield hidinfos


@pytest.fixture()
def broken_hidinfo_list(
    hidinfo_list,
) -> Generator[Dict[str, Union[bytes, int, str]], None, None]:

    broken = []
    for item in hidinfo_list:
        del item["product_id"]
        del item["vendor_id"]
        del item["path"]
        broken.append(item)
    yield broken


@pytest.fixture(scope="session")
def real_lights() -> Generator[List[USBLight], None, None]:
    """Real instances of USBLight (if available)."""

    lights = USBLight.all_lights()

    yield lights

    with suppress(IndexError):
        while light := lights.pop():
            del light


@pytest.fixture(scope="session")
def synthetic_lights() -> Generator[List[USBLight], None, None]:

    lights = []
    for subclass in USBLight.subclasses():
        lights.extend(synthetic_lights_for_subclass(subclass))

    yield lights

    with suppress(IndexError):
        while item := lights.pop():
            del item


@pytest.fixture(scope="session")
def lights(
    real_lights: List[USBLight],
    synthetic_lights: List[USBLight],
) -> Generator[List[USBLight], None, None]:
    """Returns real_lights if available, otherwise synthetic_lights."""
    if real_lights:
        yield real_lights
    else:
        yield synthetic_lights


@pytest.fixture()
def disposable_lights() -> Generator[List[USBLight], None, None]:
    """Disposable lights are synthetic but function scoped. Mess'em up."""
    lights = []
    for subclass in USBLight.subclasses():
        lights.extend(synthetic_lights_for_subclass(subclass))
    yield lights

    with suppress(IndexError):
        while item := lights.pop():
            del item


@pytest.fixture(scope="session")
def a_light(lights: List[USBLight]) -> Generator[USBLight, None, None]:
    """Could be real, could be synthetic. But it's a light."""
    yield lights[0]


@pytest.fixture()
def synthetic_light_manager(synthetic_lights) -> Generator[LightManager, None, None]:

    manager = LightManager()
    manager.release()
    manager._lights = synthetic_lights

    yield manager

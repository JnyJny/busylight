"""
"""

from typing import List

import pytest

from unittest import mock

from fastapi.testclient import TestClient

from busylight.lights import USBLight
from busylight.api import busylightapi


@pytest.fixture(scope="session")
def supported_lights() -> list:
    """A list of supported USBLight subclasses."""

    return USBLight.supported_lights()


@pytest.fixture(scope="session")
def lights(supported_lights) -> list:
    """A list of instances for each supported USBLight.

    Each USBLight subclass instance has it's hid.device patched
    to simulate successful IO to the device without requiring an
    actual connected USB device.
    """

    lights = []
    for usblight in supported_lights:
        for vendor_id in usblight.VENDOR_IDS:
            try:
                product_id = usblight.PRODUCT_IDS[0]
            except IndexError:
                product_id = 0xFFFF

            class FakeHIDDevice:
                def open_path(self, *args, **kwargs):
                    return

                def write(self, data):
                    return len(data)

                def send_feature_report(self, data):
                    return len(data)

            with mock.patch("hid.device", new=FakeHIDDevice):
                lights.append(usblight(vendor_id, product_id, b"bogus_path"))
                lights[-1]._info = {
                    "vendor_id": vendor_id,
                    "product_id": product_id,
                    "path": b"bogus_path",
                    "serial_number": "BS032974-3.0",
                    "release_number": 0x200,
                }
    return lights


@pytest.fixture(scope="session")
def busylight_client() -> TestClient:
    return TestClient(busylightapi)


@pytest.fixture(scope="session")
def busylight_api_routes(busylight_client) -> List[str]:

    with busylight_client as client:
        response = client.get("/")

    return [r["path"] for r in response.json()]

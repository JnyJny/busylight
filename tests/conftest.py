"""
"""

import pytest

from unittest import mock

from busylight.lights import USBLight


@pytest.fixture(scope="session")
def supported_lights() -> list:
    """A list of supported USBLight subclasses."""

    return USBLight.supported_lights()


@pytest.fixture
def lights() -> list:
    """A list of instances for each supported USBLight.

    Each USBLight subclass instance has it's hid.device patched
    to simulate successful IO to the device without requiring an
    actual connected USB device.
    """

    lights = []
    for usblight in USBLight.supported_lights():
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
    return lights

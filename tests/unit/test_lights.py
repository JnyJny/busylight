"""
"""

import pytest

from busylight.lights.usblight import USBLight

from busylight.lights import SUPPORTED_LIGHTS
from busylight.lights import KNOWN_VENDOR_IDS


def test_busylight_lights_imported_supported_lights():
    assert isinstance(SUPPORTED_LIGHTS, list)


def test_busylight_lights_imported_known_vendor_ids():
    assert isinstance(KNOWN_VENDOR_IDS, list)


@pytest.mark.parametrize("light", SUPPORTED_LIGHTS)
def test_busylight_lights_check_supported_lights(light):

    assert issubclass(light, USBLight)
    assert hasattr(light, "__vendor__")
    assert hasattr(light, "VENDOR_IDS")
    assert hasattr(light, "impl_on")
    assert hasattr(light, "impl_off")
    assert hasattr(light, "impl_blink")


@pytest.mark.parametrize("vendor_id", KNOWN_VENDOR_IDS)
def test_busylight_lights_known_vendor_ids(vendor_id):

    assert isinstance(vendor_id, int)
    assert vendor_id in range(1, 65534)

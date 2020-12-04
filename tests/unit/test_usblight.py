"""
"""

import pytest

from busylight.lights import USBLight
from busylight.lights import USBLightInUse
from busylight.lights import USBLightNotFound
from busylight.lights import USBLightIOError
from busylight.lights import UnknownUSBLight


def test_usblight_classmethod_first_light():

    with pytest.raises(USBLightNotFound):
        USBLight.first_light()


@pytest.mark.parametrize(
    "given",
    [
        {},
        {"vendor_id": 0},
        {"product_id": 0},
        {"foo": 0, "baz": 1},
    ],
)
def test_usblight_classmethod_from_dict_invalid(given):

    with pytest.raises(ValueError):
        USBLight.from_dict(given)


def test_usblight_classmethod_from_dict():

    with pytest.raises(UnknownUSBLight):
        USBLight.from_dict({"vendor_id": 0, "product_id": 0, "path": b""})


def test_usblight_init():

    with pytest.raises(UnknownUSBLight):
        USBLight(0, 0, b"")


def test_usblight_attributes(generic_usblight):

    assert generic_usblight.vendor_id == 0xFFFF
    assert generic_usblight.product_id == 0xFFFF
    assert generic_usblight.path == b"bogus_path"
    assert generic_usblight.value == 0xDEADBEEF
    assert generic_usblight.default_state == 0xDEADBEEF
    assert len(generic_usblight) == 128

    assert hasattr(generic_usblight, "VENDOR_IDS")
    assert len(generic_usblight.VENDOR_IDS) == 0
    assert generic_usblight.__vendor__ == "generic"

    assert not hasattr(generic_usblight, "impl_on")
    assert not hasattr(generic_usblight, "impl_off")
    assert not hasattr(generic_usblight, "impl_blink")


#    assert generic_usblight.

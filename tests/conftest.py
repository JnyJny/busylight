"""
"""

import pytest

from unittest import mock

from busylight.lights.usblight import USBLight

from busylight.lights.agile_innovations import BlinkStick
from busylight.lights.embrava import Blynclight
from busylight.lights.kuando import BusyLight
from busylight.lights.luxafor import Flag
from busylight.lights.thingm import Blink1


@pytest.fixture
def generic_usblight():
    """"""
    USBLight.VENDOR_IDS.append(0xFFFF)
    with mock.patch("hid.device"):
        light = USBLight(0xFFFF, 0xFFFF, b"bogus_path", 0xDEAD_BEEF)
    USBLight.VENDOR_IDS.remove(0xFFFF)
    return light


@pytest.fixture
def blinkstick():
    """busylight.lights.agile_innovations.BlinkStick fixture whose product_id is 0xFFFF."""
    try:
        return BlinkStick.first_light()
    except USBLightNotFound:
        pass
    vendor_id = BlinkStick.VENDOR_IDS[0]
    with mock.patch("hid.device"):
        light = BlinkStick(vendor_id, 0xFFFF, b"bogus_path")
    return light


@pytest.fixture
def blynclight():
    """busylight.lights.embrava.BlyncLight fixture whose product_id is 0xFFFF."""
    try:
        return Blynclight.first_light()
    except USBLightNotFound:
        pass
    vendor_id = Blynclight.VENDOR_IDS[0]
    with mock.patch("hid.device"):
        light = Blynclight(vendor_id, 0xFFFF, b"bogus_path")
    return light


@pytest.fixture
def busylight():
    """busylight.lights.kuando.BusyLight fixture whose product_id is 0xFFFF."""
    try:
        return BusyLight.first_light()
    except USBLightNotFound:
        pass
    vendor_id = BusyLight.VENDOR_IDS[0]
    with mock.patch("hid.device"):
        light = BusyLight(vendor_id, 0xFFFF, b"bogus_path")
    return light


@pytest.fixture
def flag():
    """busylight.lights.luxafor.Flag fixture whose product_id is 0xFFFF."""
    try:
        return Flag.first_light()
    except USBLightNotFound:
        pass
    vendor_id = Flag.VENDOR_IDS[0]
    with mock.patch("hid.device"):
        light = Flag(vendor_id, 0xFFFF, b"bogus_path")
    return light


@pytest.fixture
def blink1():
    """busylight.lights.thingm.Blink1 fixture whose product_id is 0xFFFF."""
    try:
        return Blink1.first_light()
    except USBLightNotFound:
        pass
    vendor_id = Blink1.VENDOR_IDS[0]
    with mock.patch("hid.device"):
        light = Blink1(vendor_id, 0xFFFF, b"bogus_path")
    return light

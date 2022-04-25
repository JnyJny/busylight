"""
"""

from contextlib import suppress
from typing import Callable, List
from unittest import mock
from unittest.mock import Mock, PropertyMock

import hid
import pytest

from busylight.lights import (
    USBLight,
    LightUnavailable,
    LightUnsupported,
)

from .. import is_valid_hidinfo


## Data model methods


def test_usblight_subclass_repr(synthetic_lights) -> None:
    """Test the __repr__ method to ensure a str is returned."""
    for light in synthetic_lights:
        result = repr(light)
        assert isinstance(result, str)


def test_usblight_subclass_str(synthetic_lights) -> None:
    """Test the __str__ method to ensure a str is returned."""
    for light in synthetic_lights:
        result = str(light)
        assert isinstance(result, str)


def test_usblight_del(disposable_lights) -> None:
    """Test the __del__ method to ensure it doesn't barf."""
    with pytest.raises(IndexError):
        while light := disposable_lights.pop():
            del light


def test_usblight_eq(synthetic_lights) -> None:
    """Test the __eq__ method for functionality."""
    assert synthetic_lights[0] == synthetic_lights[0]
    assert synthetic_lights[0] != synthetic_lights[1]
    assert synthetic_lights[1] == synthetic_lights[1]
    assert synthetic_lights[1] != synthetic_lights[0]


def test_usblight_lt(synthetic_lights) -> None:
    """Test the __lt__ method to confirm sortability of lists of lights."""
    lights = sorted(synthetic_lights)
    for a, b in zip(lights[:-1], lights[1:]):
        assert a < b


## Instance properties


def test_usblight_repr(synthetic_lights) -> None:
    """Test the __repr__ method to ensure a str is returned."""
    for light in synthetic_lights:
        result = repr(light)
        assert isinstance(result, str)
        assert result.startswith(light.__class__.__name__)


def test_usblight_hidinfo(synthetic_lights) -> None:
    """Checks the hidinfo property for validity."""
    for light in synthetic_lights:
        assert is_valid_hidinfo(light.hidinfo)


@pytest.mark.parametrize(
    "property_name,expected_type",
    [
        ("hidinfo", dict),
        ("vendor_id", int),
        ("product_id", int),
        ("path", str),
        ("product_string", str),
        ("serial_number", str),
        ("release_number", int),
        ("manufacturer_string", str),
        ("usage_page", int),
        ("usage", int),
        ("write_strategy", Callable),
        ("read_strategy", Callable),
        ("is_pluggedin", bool),
        ("is_unplugged", bool),
        ("red", int),
        ("green", int),
        ("blue", int),
        ("color", tuple),
    ],
)
def test_usblight_properties(
    property_name: str, expected_type: type, synthetic_lights: List[USBLight]
) -> None:
    for light in synthetic_lights:
        assert hasattr(light, property_name)
        value = getattr(light, property_name)
        assert isinstance(value, expected_type)


def test_usblight_plugged(disposable_lights) -> None:

    for light in disposable_lights:
        assert light.is_pluggedin
        assert not light.is_unplugged


def test_usblight_unplugged(disposable_lights) -> None:

    for light in disposable_lights:
        error = OSError("read error on unplugged device")
        light.device.read.side_effect = error
        light.device.get_feature_report.side_effect = error
        assert not light.is_pluggedin
        assert light.is_unplugged


COLOR_TEST_VALUES = [
    # value, expected
    (0xFF, 0xFF),
    (0x80, 0x80),
    (0, 0),
    (256, 0xFF),
    (-1, 0),
]


@pytest.mark.parametrize("value,expected", COLOR_TEST_VALUES)
def test_usblight_red(value, expected, a_light) -> None:
    a_light.red = value
    assert a_light.red == expected
    assert a_light.color[0] == expected


@pytest.mark.parametrize("value,expected", COLOR_TEST_VALUES)
def test_usblight_green(value, expected, a_light) -> None:
    a_light.green = value
    assert a_light.green == expected
    assert a_light.color[1] == expected


@pytest.mark.parametrize("value,expected", COLOR_TEST_VALUES)
def test_usblight_blue(value, expected, a_light) -> None:
    a_light.blue = value
    assert a_light.blue == expected
    assert a_light.color[2] == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ((255, 255, 255), (255, 255, 255)),
        ((0, 0, 0), (0, 0, 0)),
        ((128, 128, 128), (128, 128, 128)),
        ((256, 256, 256), (255, 255, 255)),
        ((-1, -1, -1), (0, 0, 0)),
    ],
)
def test_usblight_color(value, expected, a_light) -> None:

    a_light.color = value
    assert a_light.color == expected
    assert a_light.red == expected[0]
    assert a_light.green == expected[1]
    assert a_light.blue == expected[2]


@pytest.mark.parametrize(
    "value",
    [
        "a",
        "#000",
        "#000000",
        "blue",
        1.0,
        [],
        {},
        (),
        (0,),
        (0, 0),
        (0, 0, 0, 0),
    ],
)
def test_usblight_color_malformed(value, a_light) -> None:

    with pytest.raises(ValueError):
        a_light.color = value


## Instance methods


def test_usblight_reset(disposable_lights) -> None:

    for light in disposable_lights:
        light.color = (0xFF, 0xEE, 0xDD)
        light.reset()
        assert light.color == (0, 0, 0)

        if light.device.write.called:
            light.device.write.assert_called_once()
            return

        if light.device.send_feature_report.called:
            light.device.send_feature_report.assert_called_once()
            return

    assert False, "light.reset() did not result in expected IO operations"


def test_usblight_release(disposable_lights) -> None:

    for light in disposable_lights:
        light.release()
        light.device.read.side_effect = OSError("read while closed")
        light.device.send_feature_report.side_effect = OSError("read while closed")
        with pytest.raises(OSError):
            light.read_strategy(8)


def test_usblight_batch_update(disposable_lights) -> None:

    for light in disposable_lights:

        with light.batch_update():
            pass

        if light.device.write.called:
            light.device.write.assert_called_once()
            return

        if light.device.send_feature_report.called:
            light.device.send_feature_report.assert_called_once()
            return

    assert False, "light.batch_update() did not result in expected IO operations"


def test_usblight_batch_update_unplugged(disposable_lights) -> None:

    for light in disposable_lights:

        light.device.write.return_value = -1
        light.device.send_feature_report.return_value = -1

        with pytest.raises(LightUnavailable):
            with light.batch_update():
                pass


def test_usblight_update(disposable_lights) -> None:

    for light in disposable_lights:

        light.update()

        if light.device.write.called:
            light.device.write.assert_called_once()
            return

        if light.device.send_feature_report.called:
            light.device.send_feature_report.assert_called_once()
            return

    assert False, "light.update() did not result in expected IO operations"


def test_usblight_update_unavailable(disposable_lights) -> None:

    for light in disposable_lights:

        light.device.write.return_value = -1
        light.device.send_feature_report.return_value = -1

        with pytest.raises(LightUnavailable):
            light.update()


def test_usblight_update_closed(disposable_lights) -> None:

    for light in disposable_lights:
        error = ValueError("write on a closed device")
        light.device.write.side_effect = error
        light.device.send_feature_report.side_effect = error
        with pytest.raises(LightUnavailable):
            light.update()


def test_usblight_acquire(disposable_lights) -> None:

    for light in disposable_lights:
        light.release()
        light._device = Mock()
        light.acquire()
        light.device.open_path.assert_called_once()


def test_usblight_acquire_unavailable(disposable_lights) -> None:

    for light in disposable_lights:
        light.device.open_path.side_effect = OSError("nope")
        with pytest.raises(LightUnavailable):
            light.acquire()


def test_usblight_reset(disposable_lights) -> None:

    for light in disposable_lights:
        light.color = (0xF, 0xE, 0xD)
        light.reset()
        assert light.color == (0, 0, 0)


@pytest.mark.parametrize(
    "color",
    [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
    ],
)
def test_usblight_on(color, disposable_lights):

    for light in disposable_lights:
        light.color = (0, 0, 0)
        assert light.is_off
        assert not light.is_on
        assert light.color != color
        light.on(color)
        assert light.color == color
        assert light.is_on
        assert not light.is_off

        if light.device.write.called:
            light.device.write.assert_called_once()
            return

        if light.device.send_feature_report.called:
            light.device.send_feature_report.assert_called_once()
            return

        assert False, "light.on(...) resulted in no IO operations"


def test_usblight_off(disposable_lights):

    for light in disposable_lights:
        light.off()
        assert light.is_off
        assert not light.is_on
        if light.device.write.called:
            light.device.write.assert_called_once()
            return

        if light.device.send_feature_report.called:
            light.device.send_feature_report.assert_called_once()
            return

        assert False, "light.off() resulted in no IO operations"

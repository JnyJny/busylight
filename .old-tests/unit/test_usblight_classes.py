""" test USBLight classmethods and __init__
"""

from unittest import mock

import pytest

from busylight.lights import (
    InvalidHidInfo,
    LightNotFound,
    LightUnavailable,
    LightUnsupported,
    NoLightsFound,
)

from busylight.lights import USBLight

from .. import (
    is_valid_hidinfo,
    device_hidinfo,
    device_hidinfo_unknown,
)


USBLIGHT_SUBCLASSES = USBLight.subclasses()
ALL_USBLIGHT_CLASSES = [USBLight] + USBLIGHT_SUBCLASSES


## Classmethods


@pytest.mark.parametrize("subclass", ALL_USBLIGHT_CLASSES)
def test_usblight_available(subclass) -> None:

    results = subclass.available()
    assert isinstance(results, list)
    for item in results:
        assert is_valid_hidinfo(item)


def test_usblight_claims(hidinfo_list) -> None:

    for hidinfo in hidinfo_list:
        assert USBLight.claims(hidinfo)


def test_usblight_claims_broken(broken_hidinfo_list) -> None:

    for hidinfo in broken_hidinfo_list:
        with pytest.raises(InvalidHidInfo):
            USBLight.claims(hidinfo)


@pytest.mark.parametrize("subclass", ALL_USBLIGHT_CLASSES)
def test_usblight_supported_lights(subclass) -> None:

    results = subclass.supported_lights()

    assert isinstance(results, dict)
    for key, value in results.items():
        assert isinstance(key, str)
        assert isinstance(value, list)
        for item in value:
            assert isinstance(item, str)


@pytest.mark.parametrize("subclass", ALL_USBLIGHT_CLASSES)
def test_usblight_subclasses(subclass) -> None:

    results = subclass.subclasses()
    assert isinstance(results, list)
    for item in results:
        assert issubclass(item, subclass)


@pytest.mark.parametrize("subclass", ALL_USBLIGHT_CLASSES)
def test_usblight_all_lights(subclass, hidinfo_list) -> None:

    with mock.patch("hid.enumerate") as mock_enumerate:
        mock_enumerate.return_value = hidinfo_list
        results = subclass.all_lights()
        assert isinstance(results, list)
        for item in results:
            assert issubclass(type(item), subclass)


@pytest.mark.parametrize("subclass", ALL_USBLIGHT_CLASSES)
def test_usblight_all_lights_unavailable(subclass) -> None:

    with mock.patch("hid.enumerate") as mock_enumerate:
        mock_enumerate.return_value = []
        results = subclass.all_lights()
        assert isinstance(results, list)
        assert not results


@pytest.mark.parametrize("subclass", ALL_USBLIGHT_CLASSES)
def test_usblight_first_light(subclass, hidinfo_list) -> None:

    with mock.patch("hid.enumerate") as mock_enumerate:
        mock_enumerate.return_value = hidinfo_list
        with pytest.raises(LightUnavailable):
            # EJO The lights described in hidinfo_list are a static dump
            #     and the embedded paths are invalid. I'm going to avoid
            #     trying to mock `hid.device.open` to get the call to
            #     first_light to succeed. It's just too much of a PITA
            #     for me right now.
            subclass.first_light()


@pytest.mark.parametrize("subclass", ALL_USBLIGHT_CLASSES)
def test_usblight_first_light_no_lights(subclass, hidinfo_list) -> None:

    with mock.patch("hid.enumerate") as mock_enumerate:
        mock_enumerate.return_value = {}
        with pytest.raises(NoLightsFound):
            subclass.first_light()


@pytest.mark.parametrize("subclass", ALL_USBLIGHT_CLASSES)
def test_usblight_udev_rules_default(subclass) -> None:
    results = subclass.udev_rules()
    assert isinstance(results, list)
    for item in results:
        assert isinstance(item, str)


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_usblight_from_dict_known(subclass) -> None:

    with mock.patch("hid.device") as mock_device:
        with mock.patch("hid.enumerate") as mock_enumerate:

            for hidinfo in device_hidinfo(subclass):
                result = USBLight.from_dict(hidinfo, reset=False)
                assert isinstance(result, subclass)


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_usblight_from_dict_subclass_known(subclass) -> None:

    with mock.patch("hid.device") as mock_device:
        with mock.patch("hid.enumerate") as mock_enumerate:
            for hidinfo in device_hidinfo(subclass):
                result = subclass.from_dict(hidinfo, reset=False)
                assert isinstance(result, subclass)


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_usblight_from_dict_unknown(subclass) -> None:
    for hidinfo in device_hidinfo_unknown(subclass):
        with pytest.raises(LightUnsupported):
            result = USBLight.from_dict(hidinfo, reset=False)


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_usblight_from_dict_subclass_unknown(subclass) -> None:
    for hidinfo in device_hidinfo_unknown(subclass):
        with pytest.raises(LightUnsupported):
            result = subclass.from_dict(hidinfo, reset=False)


## Initializing instances


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_usblight_init(subclass) -> None:

    for hidinfo in device_hidinfo(subclass):
        with pytest.raises(TypeError):
            USBLight(hidinfo, False)
        with pytest.raises(TypeError):
            USBLight(hidinfo, False)

    for hidinfo in device_hidinfo_unknown(subclass):
        with pytest.raises(TypeError):
            USBLight(hidinfo, False)
        with pytest.raises(TypeError):
            USBLight(hidinfo, False)


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_usblight_init_without_reset(subclass) -> None:

    for hidinfo in device_hidinfo(subclass):
        with mock.patch("hid.device") as mock_device:
            result = subclass(hidinfo, reset=False)
            assert isinstance(result, subclass)


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_usblight_init_with_reset(subclass) -> None:

    for hidinfo in device_hidinfo(subclass):
        with mock.patch("hid.device"):
            with mock.patch("busylight.lights.USBLight.reset") as mock_reset:
                result = subclass(hidinfo, reset=True)
                assert isinstance(result, subclass)
                mock_reset.assert_called_once()


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_usblight_init_hidinfo_missing_path(subclass) -> None:

    for hidinfo in device_hidinfo(subclass):
        del hidinfo["path"]
        with pytest.raises(InvalidHidInfo):
            subclass(hidinfo)


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_usblight_init_unknown(subclass) -> None:
    for hidinfo in device_hidinfo_unknown(subclass):
        with pytest.raises(LightUnsupported):
            result = subclass(hidinfo)

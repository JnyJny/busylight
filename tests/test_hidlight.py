"""test busylight.lights.HIDLight class"""

import busylight.lights.hidlight
import pytest
from busylight.lights import NoLightsFound
from busylight.lights.hidlight import HIDLight

from . import HID_LIGHTS, NOT_A_LIGHT, SERIAL_LIGHTS, MockDevice


@pytest.mark.parametrize("light_info", HID_LIGHTS)
def test_hidlight_available_offline_good(light_info, mocker) -> None:
    mocker.patch("hid.enumerate", return_value=[light_info])

    result = HIDLight.available_lights()

    assert isinstance(result, list)
    assert len(result) == 1

    assert result[0]["vendor_id"] == light_info["vendor_id"]
    assert result[0]["product_id"] == light_info["product_id"]
    assert result[0]["path"] == light_info["path"]
    assert "device_id" in result[0]
    assert result[0]["device_id"] == (light_info["vendor_id"], light_info["product_id"])


def test_hidlight_available_offline_no_lights(mocker) -> None:
    mocker.patch("hid.enumerate", return_value=[])

    result = HIDLight.available_lights()

    assert isinstance(result, list)
    assert len(result) == 0


KNOWN_BAD_LIGHTS = [
    {"vendor_id": 0x0, "product_id": 0x0, "path": b"/fake/path"},
    {"vendor_id": 0x2C0D},
    {"product_id": 0x0001},
    {"path": b"fake_path"},
]


@pytest.mark.parametrize("light_info", KNOWN_BAD_LIGHTS)
def test_hidlight_available_offline_malformed(light_info, mocker) -> None:
    mocker.patch("hid.enumerate", return_value=[light_info])

    result = HIDLight.available_lights()

    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.parametrize("light_info", HID_LIGHTS)
def test_hidlight_all_lights_offline_good(light_info, mocker) -> None:
    mocker.patch("hid.enumerate", return_value=[light_info])

    mocker.patch("busylight.lights.hidlight.HIDLight.device", MockDevice)

    result = HIDLight.all_lights()  # reset=False, exclusive=False)

    assert isinstance(result, list)
    assert len(result) == 1

    assert isinstance(result[0], HIDLight)


def test_hidlight_first_light_offline_no_lights(mocker) -> None:
    mocker.patch("hid.enumerate", return_value=[])

    with pytest.raises(NoLightsFound):
        result = HIDLight.first_light()


@pytest.mark.parametrize("light_info", HID_LIGHTS)
def test_hidlight_first_light_offline_good(light_info, mocker) -> None:
    mocker.patch("hid.enumerate", return_value=[light_info])

    mocker.patch("busylight.lights.hidlight.HIDLight.device", MockDevice)

    result = HIDLight.first_light()

    assert isinstance(result, HIDLight)


@pytest.mark.parametrize("light_info", HID_LIGHTS)
def test_hidlight_claims_offline_claimed(light_info) -> None:
    result = HIDLight.claims(light_info)

    assert result


@pytest.mark.parametrize("light_info", SERIAL_LIGHTS + NOT_A_LIGHT)
def test_hidlight_claims_offline_not_claimed(light_info):
    result = HIDLight.claims(light_info)

    assert not result


def test_hidlight_supported_lights() -> None:
    result = HIDLight.supported_lights()

    assert isinstance(result, dict)
    for key, value in result.items():
        assert isinstance(key, str)
        assert isinstance(value, list)
        for item in value:
            assert isinstance(item, str)


def test_hidlight__is_abstract() -> None:
    result = HIDLight._is_abstract()

    assert result


def test_hidlight__is_physical() -> None:
    result = HIDLight._is_physical()

    assert not result


@pytest.mark.parametrize("light_info", HID_LIGHTS)
def test_hidlight_init_fails_for_abc(light_info, mocker) -> None:
    with pytest.raises(TypeError):
        HIDLight(light_info, reset=True, exclusive=True)

"""test busylight.lights.SerialLight class"""

import busylight.lights.seriallight
import pytest
from busylight.lights import NoLightsFound
from busylight.lights.seriallight import SerialLight
from serial.tools.list_ports_common import ListPortInfo

from . import HID_LIGHTS, NOT_A_LIGHT, SERIAL_LIGHTS, MockDevice


def listportinfo(light_info: dict) -> ListPortInfo:
    port_info = ListPortInfo(light_info["path"], skip_link_detection=True)

    port_info.vid = light_info["vendor_id"]
    port_info.pid = light_info["product_id"]
    port_info.serial_number = "fake serial number"
    port_info.description = light_info["product_string"]
    port_info.manufacturer = "fake manufacturer"

    return port_info


@pytest.mark.parametrize("light_info", SERIAL_LIGHTS)
def test_seriallight_available_offline_good(light_info, mocker) -> None:
    mocker.patch(
        "serial.tools.list_ports.comports",
        return_value=[listportinfo(light_info)],
    )

    result = SerialLight.available_lights()

    assert isinstance(result, list)
    assert len(result) == 1

    assert result[0]["vendor_id"] == light_info["vendor_id"]
    assert result[0]["product_id"] == light_info["product_id"]
    assert result[0]["path"] == light_info["path"]
    assert "device_id" in result[0]
    assert result[0]["device_id"] == (light_info["vendor_id"], light_info["product_id"])


def test_seriallight_available_offline_no_lights(mocker) -> None:
    mocker.patch(
        "serial.tools.list_ports.comports",
        return_value=[],
    )

    result = SerialLight.available_lights()

    assert isinstance(result, list)
    assert len(result) == 0


KNOWN_BAD_LIGHTS = [
    {"vendor_id": 0x0, "product_id": 0x0, "path": b"/fake/path"},
    {"vendor_id": 0x2C0D},
    {"product_id": 0x0001},
    {"path": b"fake_path"},
]


def test_seriallight_available_offline_malformed(mocker) -> None:
    portinfos = [
        ListPortInfo("/bogus/path", skip_link_detection=True),
        ListPortInfo("/fake/path", skip_link_detection=True),
    ]

    mocker.patch(
        "serial.tools.list_ports.comports",
        return_value=portinfos,
    )

    result = SerialLight.available_lights()

    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.parametrize("light_info", SERIAL_LIGHTS)
def test_seriallight_all_lights_offline_good(light_info, mocker) -> None:
    mocker.patch(
        "serial.tools.list_ports.comports",
        return_value=[listportinfo(light_info)],
    )

    mocker.patch("busylight.lights.seriallight.SerialLight.device", MockDevice)

    result = SerialLight.all_lights()  # reset=False, exclusive=False)

    assert isinstance(result, list)
    assert len(result) == 1

    assert isinstance(result[0], SerialLight)


def test_seriallight_first_light_offline_no_lights(mocker) -> None:
    mocker.patch("serial.tools.list_ports.comports", return_value=[])

    with pytest.raises(NoLightsFound):
        result = SerialLight.first_light()


@pytest.mark.parametrize("light_info", SERIAL_LIGHTS)
def test_seriallight_first_light_offline_good(light_info, mocker) -> None:
    mocker.patch(
        "serial.tools.list_ports.comports",
        return_value=[listportinfo(light_info)],
    )

    mocker.patch("busylight.lights.seriallight.SerialLight.device", MockDevice)

    result = SerialLight.first_light()

    assert isinstance(result, SerialLight)


@pytest.mark.parametrize("light_info", SERIAL_LIGHTS)
def test_seriallight_claims_offline_claimed(light_info) -> None:
    result = SerialLight.claims(light_info)

    assert result


@pytest.mark.parametrize("light_info", HID_LIGHTS + NOT_A_LIGHT)
def test_seriallight_claims_offline_not_claimed(light_info):
    result = SerialLight.claims(light_info)

    assert not result


def test_seriallight_supported_lights() -> None:
    result = SerialLight.supported_lights()

    assert isinstance(result, dict)
    for key, value in result.items():
        assert isinstance(key, str)
        assert isinstance(value, list)
        for item in value:
            assert isinstance(item, str)


def test_seriallight__is_abstract() -> None:
    result = SerialLight._is_abstract()

    assert result


def test_seriallight__is_physical() -> None:
    result = SerialLight._is_physical()

    assert not result


@pytest.mark.parametrize("light_info", SERIAL_LIGHTS)
def test_seriallight_init_fails_for_abc(light_info, mocker) -> None:
    with pytest.raises(TypeError):
        SerialLight(light_info, reset=True, exclusive=True)

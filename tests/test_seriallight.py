"""test busylight.lights.SerialLight class
"""

import pytest

import busylight.lights.seriallight

from busylight.lights.seriallight import SerialLight

from busylight.lights import NoLightsFound

from serial.tools.list_ports_common import ListPortInfo

from . import HID_LIGHTS, SERIAL_LIGHTS


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


class MockSerialDevice:
    def open_path(self, *args) -> None:
        pass

    def read(self, *args) -> bytes:
        return bytes([0] * 8)

    def write(self, *args) -> int:
        pass

    def send_feature_report(self, *args) -> int:
        pass

    def get_feature_report(self, *args) -> list[int]:
        return [0]


@pytest.mark.xfail
@pytest.mark.parametrize("light_info", SERIAL_LIGHTS)
def test_seriallight_all_lights_offline_good(light_info, mocker) -> None:

    mocker.patch("hid.enumerate", return_value=[light_info])

    mocker.patch("busylight.lights.hidlight.SerialLight.device", MockHidDevice)

    result = SerialLight.all_lights()  # reset=False, exclusive=False)

    assert isinstance(result, list)
    assert len(result) == 1

    assert isinstance(result[0], SerialLight)


@pytest.mark.xfail
def test_seriallight_first_light_offline_no_lights(mocker) -> None:

    mocker.patch("hid.enumerate", return_value=[])

    with pytest.raises(NoLightsFound):
        result = SerialLight.first_light()


@pytest.mark.xfail
@pytest.mark.parametrize("light_info", SERIAL_LIGHTS)
def test_seriallight_first_light_offline_good(light_info, mocker) -> None:

    mocker.patch("hid.enumerate", return_value=[light_info])

    mocker.patch("busylight.lights.hidlight.SerialLight.device", MockSerialDevice)

    result = SerialLight.first_light()

    assert isinstance(result, SerialLight)


@pytest.mark.xfail
@pytest.mark.parametrize("light_info", SERIAL_LIGHTS)
def test_seriallight_claims_offline_claimed(light_info) -> None:

    light_info["device_id"] = (light_info["vendor_id"], light_info["product_id"])

    result = SerialLight.claims(light_info)

    assert result


@pytest.mark.xfail
@pytest.mark.parametrize("light_info", HID_LIGHTS)
def test_seriallight_claims_offline_not_claimed(light_info):

    light_info["device_id"] = (light_info["vendor_id"], light_info["product_id"])

    result = SerialLight.claims(light_info)
    assert not result


@pytest.mark.xfail
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


@pytest.mark.xfail
def test_seriallight_udev_rules() -> None:

    result = SerialLight.udev_rules()
    assert isinstance(result, list)

    for item in result:
        assert isinstance(item, str)

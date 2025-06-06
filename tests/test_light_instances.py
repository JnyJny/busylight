"""Test initializing instances of Light subclasses"""

import busylight.lights.agile_innovative.blinkstick
import busylight.lights.compulab.fit_statusb
import busylight.lights.embrava.blynclight
import busylight.lights.embrava.blynclight_mini
import busylight.lights.embrava.blynclight_plus
import busylight.lights.kuando.busylight_alpha
import busylight.lights.kuando.busylight_omega
import busylight.lights.luxafor.bluetooth
import busylight.lights.luxafor.flag
import busylight.lights.luxafor.mute
import busylight.lights.luxafor.orb
import pytest
from busylight.lights import LightUnsupported

from . import BOGUS_DEVICE_ID, PHYSICAL_LIGHT_SUBCLASSES, LightType, MockDevice


# EJO this test is broken and needs some love.
@pytest.mark.xfail
@pytest.mark.parametrize("subclass", PHYSICAL_LIGHT_SUBCLASSES)
def test_light_instance_init_known_good_lights(subclass: LightType, mocker) -> None:
    """Initialize a Light subclass with known good light_info dictionaries."""

    mocker.patch(subclass.device, MockDevice)

    light_info = {
        # EJO Easier to pre-populate this dictionary with these values
        #     for Agile Innovative BlinkStick than to discover
        #     them. All other physical lights will ignore them.
        "serial_number": "BS032974-3.0",
        "release_number": 0x0200,
    }

    for key, value in subclass.supported_device_ids().items():
        light_info["device_id"] = key
        light_info["product_string"] = value
        light = subclass(light_info)

        assert isinstance(light, subclass)


@pytest.mark.parametrize("subclass", PHYSICAL_LIGHT_SUBCLASSES)
def test_light_instance_init_known_bad_lights(subclass: LightType) -> None:
    """Initialize a Light subclass with known bad light_info dictionaries."""

    light_info = {
        "serial_number": "bogus serial number",
        "release_number": 0x0,
        "device_id": BOGUS_DEVICE_ID,
        "product_string": "nonexistent light",
    }

    with pytest.raises(LightUnsupported):
        light = subclass(light_info, reset=False, exclusive=False)

"""
"""

import pytest

from busylight.lights import USBLight

from busylight.manager import BlinkSpeed
from busylight.manager import LightManager
from busylight.manager import LightIdRangeError
from busylight.manager import ColorLookupError


def test_blink_speed_enumeration():

    for value, speed in enumerate(BlinkSpeed, start=1):
        assert speed.to_numeric_value() == value


@pytest.mark.skip(reason="Induces crash in python somehow")
def test_lightmanager_available_classmethod():

    result = LightManager.available()
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, USBLight)


@pytest.fixture(scope="session")
def manager():
    return LightManager()


@pytest.mark.skip(reason="Induces crash in python somehow")
def test_lightmanager_check_attributes(manager):

    assert hasattr(manager, "supported")
    assert isinstance(manager.supported, list)
    assert hasattr(manager, "lights")
    assert isinstance(manager.lights, list)
    assert hasattr(manager, "lights_for")
    assert isinstance(manager.lights_for(-1), list)
    assert hasattr(manager, "update")
    assert hasattr(manager, "release")
    assert hasattr(manager, "light_on")
    assert hasattr(manager, "light_off")
    assert hasattr(manager, "light_blink")
    assert hasattr(manager, "apply_effect_to_light")
    assert hasattr(manager, "operate_on")


def test_lightmanager_lights_for_range_error(manager):

    nlights = len(manager.lights)

    with pytest.raises(LightIdRangeError):
        manager.lights_for(nlights + 1)


def test_lightmanager_lights_for_all(manager):

    all_lights = manager.lights_for(-1)
    assert isinstance(all_lights, list)
    assert len(all_lights) == len(manager.lights)


@pytest.mark.parametrize("color", ["n0thex", "0xn0thex", "#n0thex", "#n0t", "0xn0t"])
def test_lightmanger_lights_on_bad_color(color, manager):

    with pytest.raises(ColorLookupError):
        manager.light_on(-1, color)

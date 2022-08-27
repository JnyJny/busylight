"""
"""

from typing import Generator
from unittest import mock

import pytest

from busylight.manager import LightManager
from busylight.lights import USBLight, NoLightsFound

from .. import device_hidinfo

from .test_usblight_classes import ALL_USBLIGHT_CLASSES, USBLIGHT_SUBCLASSES


@pytest.fixture()
def synthetic_light_manager(synthetic_lights) -> Generator[USBLight, None, None]:

    manager = LightManager()

    manager._lights = list(synthetic_lights)

    yield manager


def test_light_manager_init_no_lights() -> None:

    with mock.patch("hid.enumerate") as mock_enumerate:
        mock_enumerate.return_value = []
        manager = LightManager()
        assert not manager.lights


def test_light_manager_init(hidinfo_list) -> None:

    with mock.patch("hid.enumerate") as mock_enumerate:
        mock_enumerate.return_value = hidinfo_list
        manager = LightManager(lightclass=USBLight)
        # assert not manager.lights


@pytest.mark.parametrize("subclass", USBLIGHT_SUBCLASSES)
def test_light_manager_init_subclasses(subclass) -> None:

    with mock.patch("hid.enumerate") as mock_enumerate:

        mock_enumerate.return_value = list(device_hidinfo(subclass))

        manager = LightManager(lightclass=subclass)

        # assert len(manager.lights) == len(mock_enumerate.return_value)


@pytest.mark.parametrize("subclass", [list, set, dict, int, float, tuple])
def test_light_manager_init_unknown_subclass(subclass):

    with pytest.raises(TypeError):
        LightManager(lightclass=subclass)


@pytest.mark.parametrize("value", [True, False])
def test_light_manager_init_greedy(value: bool) -> None:

    manager = LightManager(greedy=value)
    assert manager.greedy == value


def test_light_manager_init_none_lightclass() -> None:

    manager = LightManager(lightclass=None)
    assert manager.lightclass == USBLight


@pytest.mark.parametrize("value", ["foo", 0, 0.0, [], {}, (), set()])
def test_light_manager_init_not_lightclass(value) -> None:

    with pytest.raises(TypeError):
        manager = LightManager(lightclass=value)


## Data model methods


def test_light_manager_repr(synthetic_light_manager) -> None:

    result = repr(synthetic_light_manager)
    assert result
    assert isinstance(result, str)


def test_light_manager_str(synthetic_light_manager) -> None:

    result = str(synthetic_light_manager)
    assert result
    assert isinstance(result, str)


def test_light_manager_len(synthetic_light_manager, synthetic_lights) -> None:

    result = len(synthetic_light_manager)
    assert result == len(synthetic_lights)


def test_list_manager_del(synthetic_light_manager) -> None:

    del synthetic_light_manager
    with pytest.raises(UnboundLocalError):
        synthetic_light_manager


## Properties


def test_list_manager_property_lightclass(synthetic_light_manager) -> None:

    assert issubclass(synthetic_light_manager.lightclass, USBLight)


def test_list_manager_property_lights(
    synthetic_light_manager, synthetic_lights
) -> None:

    assert isinstance(synthetic_light_manager.lights, list)
    assert len(synthetic_light_manager.lights) == len(synthetic_lights)
    for item in synthetic_light_manager.lights:
        assert isinstance(item, synthetic_light_manager.lightclass)


def test_list_manager_proiperty_lightclass_readonly(synthetic_light_manager) -> None:

    with pytest.raises(AttributeError):
        synthetic_light_manager.lightclass = USBLight


## Instance methods


def test_list_manager_release(synthetic_light_manager) -> None:

    synthetic_light_manager.release()

    with pytest.raises(AttributeError):
        synthetic_light_manager._lights


@pytest.mark.parametrize("value", [None, []])
def test_list_manager_selected_lights_default(value, synthetic_light_manager) -> None:

    result = synthetic_light_manager.selected_lights(indices=value)

    for a, b in zip(result, synthetic_light_manager.lights):
        assert a == b


@pytest.mark.parametrize(
    "indices",
    [
        [0],
        [1, 2],
        [1, -1],
        [1, 0, -1],
    ],
)
def test_list_manager_selected_lights_default(indices, synthetic_light_manager) -> None:

    result = synthetic_light_manager.selected_lights(indices=indices)

    assert len(result) == len(indices)
    for item in result:
        assert isinstance(item, synthetic_light_manager.lightclass)

    for item, index in zip(result, indices):
        assert item == synthetic_light_manager.lights[index]


def test_list_manager_selected_lights_out_of_bounds(synthetic_light_manager) -> None:
    base = len(synthetic_light_manager.lights)
    with pytest.raises(NoLightsFound):
        results = synthetic_light_manager.selected_lights([base + 1])
        # assert not results


@pytest.mark.xfail
def test_list_manager_update_no_change(synthetic_light_manager) -> None:

    assert False, "Not written yet"


@pytest.mark.xfail
def test_list_manager_update_lights_removed(synthetic_light_manager) -> None:

    assert False, "Not written yet"


@pytest.mark.xfail
def test_list_manager_update_lights_added(synthetic_light_manager) -> None:

    assert False, "Not written yet"


@pytest.mark.xfail
def test_list_manager_release(synthetic_light_manager) -> None:

    assert False, "Not written yet"

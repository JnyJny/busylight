"""Test Light classmethods"""

from typing import List

import busylight.lights.light
import pytest
from busylight.lights import InvalidLightInfo, NoLightsFound

from . import (
    ABSTRACT_LIGHT_SUBCLASSES,
    ALL_LIGHT_SUBCLASSES,
    BOGUS_DEVICE_ID,
    PHYSICAL_LIGHT_SUBCLASSES,
    LightType,
)


@pytest.mark.parametrize("subclass", ALL_LIGHT_SUBCLASSES)
def test_light_subclass_subclasses(subclass: LightType) -> None:
    """Call the `subclasses` class method for all Light subclasses."""

    result = subclass.subclasses()

    assert isinstance(result, list)

    for item in result:
        assert issubclass(item, subclass)


@pytest.mark.parametrize("subclass", ALL_LIGHT_SUBCLASSES)
def test_light_subclass_supported_lights(subclass: LightType) -> None:
    """Call the `supported_lights` class method for all Light subclasses."""

    result = subclass.supported_lights()

    assert isinstance(result, dict)

    for key, values in result.items():
        assert isinstance(key, str)
        for value in values:
            assert isinstance(value, str)


@pytest.mark.parametrize("subclass", ALL_LIGHT_SUBCLASSES)
def test_light_subclass_available_lights(subclass: LightType) -> None:
    """Call the `available_lights` class method for all Light subclasses."""

    result = subclass.available_lights()

    assert isinstance(result, list)

    for item in result:
        assert isinstance(item, dict)
        for key, value in item.items():
            assert isinstance(key, str)
            assert isinstance(value, (bytes, int, str, tuple))


@pytest.mark.parametrize("subclass", PHYSICAL_LIGHT_SUBCLASSES)
def test_light_subclass_supported_device_ids(subclass: LightType) -> None:
    """Call the `supported_device_ids` static method for each physical Light subclass."""

    result = subclass.supported_device_ids()

    assert isinstance(result, dict)

    for key, value in result.items():
        assert isinstance(key, tuple)
        assert isinstance(value, str)


@pytest.mark.parametrize("subclass", ALL_LIGHT_SUBCLASSES)
def test_light_subclass_udev_rules(subclass: LightType) -> None:
    """Call the `udev_rules` class method for all Light subclasses."""
    mode = 0o0754
    result = subclass.udev_rules(mode=mode)

    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, str)
        if "MODE=" in item:
            assert f"{mode:04o}" in item


@pytest.mark.parametrize("subclass", PHYSICAL_LIGHT_SUBCLASSES)
def test_light_subclass_vendor_concrete(subclass: LightType) -> None:
    """Call the `vendor` static method for all physical Light subclasses."""

    result = subclass.vendor()

    assert isinstance(result, str)


@pytest.mark.parametrize("subclass", ABSTRACT_LIGHT_SUBCLASSES)
def test_light_subclass_vendor_abstract(subclass: LightType) -> None:
    """Call the `vendor` static method for all abstract Light subclasses."""

    with pytest.raises(NotImplementedError):
        result = subclass.vendor()


@pytest.mark.parametrize("subclass", PHYSICAL_LIGHT_SUBCLASSES)
def test_light_subclass_claims_known_good_lights(subclass: LightType) -> None:
    """Call the `claims` class methdod for all physical Light subclasses
    with known good light_info dictionaries.
    """

    light_info = {}
    for key, value in subclass.supported_device_ids().items():
        light_info["device_id"] = key
        light_info["product_string"] = value

    claimed = subclass.claims(light_info)

    assert claimed


@pytest.mark.parametrize("subclass", PHYSICAL_LIGHT_SUBCLASSES)
def test_light_subclass_claims_known_bad_lights(subclass: LightType) -> None:
    """Call the `claims` class method for all physical Light subclasses
    with known bad light_info dictionaries.
    """

    light_info = {"device_id": BOGUS_DEVICE_ID, "product_id": "nonexistent light"}

    claimed = subclass.claims(light_info)

    assert not claimed


@pytest.mark.parametrize("subclass", PHYSICAL_LIGHT_SUBCLASSES)
def test_light_subclass_claims_malformed(subclass: LightType) -> None:
    garbage = {"foo": 1, "bar": 2, "baz": 3}

    with pytest.raises(InvalidLightInfo):
        claimed = subclass.claims(garbage)


@pytest.mark.parametrize("subclass", ALL_LIGHT_SUBCLASSES)
def test_light_subclass_all_lights(subclass: LightType) -> None:
    """Call the `all_lights` class method for all Light subclasses."""

    result = subclass.all_lights(reset=False, exclusive=False)

    assert isinstance(result, list)

    for item in result:
        assert issubclass(type(item), subclass)


@pytest.mark.xfail
@pytest.mark.parametrize("subclass", ALL_LIGHT_SUBCLASSES)
def test_light_subclass_first_light(subclass: LightType) -> None:
    """Call the `first_light` class method for all Light subclasses."""

    result = subclass.first_light(reset=False, exclusive=False)

    assert isinstance(result, subclass)


@pytest.mark.parametrize("subclass", ABSTRACT_LIGHT_SUBCLASSES)
def test_light_subclass_is_abstract(subclass: LightType) -> None:
    """Check that abstract Light subclasses self-identify correctly."""

    is_abstract = subclass._is_abstract()
    is_physical = subclass._is_physical()

    assert is_abstract and not is_physical


@pytest.mark.parametrize("subclass", PHYSICAL_LIGHT_SUBCLASSES)
def test_light_subclass_is_physical(subclass: LightType) -> None:
    """Check that physical Light subclasses self-identify correctly."""

    is_abstract = subclass._is_abstract()
    is_physical = subclass._is_physical()

    assert is_physical and not is_abstract


@pytest.mark.parametrize("subclass", ALL_LIGHT_SUBCLASSES)
def test_light_subclass_unique_device_names(subclass: LightType) -> None:
    names = subclass.unique_device_names()

    assert isinstance(names, list)
    for name in names:
        assert isinstance(name, str)

"""Tests for the Light abstract base class and its methods."""

import pytest

from busylight_core import Light, NoLightsFoundError
from busylight_core.hardware import Hardware


def test_light_init_fails(hardware_devices: list[Hardware]) -> None:
    """Test that Light abstract class cannot be instantiated directly."""
    for device in hardware_devices:
        with pytest.raises(TypeError):
            Light(device)


def test_light_abstractclassmethod_supported_device_ids() -> None:
    """Test that Light.supported_device_ids returns None for abstract class."""
    assert Light.supported_device_ids == {}


def test_light_classmethod_vendor() -> None:
    """Test that Light.vendor() returns a string."""
    result = Light.vendor()
    assert isinstance(result, str)


def test_light_classmethod_unique_device_names() -> None:
    """Test that Light.unique_device_names() returns a list of strings."""
    results = Light.unique_device_names()

    for result in results:
        assert isinstance(result, str)


def test_light_classmethod_claims_bogus_device(
    hardware_devices: list[Hardware],
) -> None:
    """Test that Light abstract class doesn't claim any devices."""
    for device in hardware_devices:
        result = Light.claims(device)
        assert not result


def test_light_classmethod_subclasses() -> None:
    """Test that Light.subclasses() returns a list of Light subclasses."""
    results = Light.subclasses()

    assert isinstance(results, list)

    for item in results:
        assert issubclass(item, Light)


def test_light_classmethod_supported_lights() -> None:
    """Test that Light.supported_lights() returns a dict of vendor to product names."""
    results = Light.supported_lights()

    assert isinstance(results, dict)

    for vendor, product_names in results.items():
        assert isinstance(vendor, str)
        assert isinstance(product_names, list)

        for product_name in product_names:
            assert isinstance(product_name, str)


def test_light_classmethod_available_hardware() -> None:
    """Test that Light.available_hardware() returns a dict of subclass to devices."""
    results = Light.available_hardware()

    assert isinstance(results, dict)

    for subclass, devices in results.items():
        assert issubclass(subclass, Light)
        assert isinstance(devices, list)

        for device in devices:
            assert isinstance(device, Hardware)


def test_light_classmethod_all_lights() -> None:
    """Test that Light.all_lights() returns a list of Light instances."""
    results = Light.all_lights(reset=False, exclusive=False)

    assert isinstance(results, list)

    for item in results:
        assert isinstance(item, Light)


def test_light_classmethod_first_light() -> None:
    """Test Light.first_light() returns a Light instance or raises NoLightsFoundError."""
    try:
        result = Light.first_light(reset=False, exclusive=False)
        assert isinstance(result, Light)
    except NoLightsFoundError:
        pass

"""Test implementation compliance across all vendor Light subclasses."""

from collections.abc import Callable

import pytest

from busylight_core import HardwareUnsupportedError, NoLightsFoundError
from busylight_core.hardware import Hardware
from busylight_core.vendors.agile_innovative.agile_innovative_base import (
    AgileInnovativeBase,
)
from busylight_core.vendors.compulab.compulab_base import CompuLabBase
from busylight_core.vendors.embrava.embrava_base import EmbravaBase
from busylight_core.vendors.epos.epos_base import EPOSBase
from busylight_core.vendors.kuando.kuando_base import KuandoBase
from busylight_core.vendors.luxafor.luxafor_base import LuxaforBase
from busylight_core.vendors.muteme.muteme_base import MuteMeBase
from busylight_core.vendors.plantronics.plantronics_base import PlantronicsBase
from busylight_core.vendors.thingm.thingm_base import ThingMBase

from vendor_examples import HardwareCatalog

VENDOR_SUBCLASSES = HardwareCatalog.keys()


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_supported_device_ids(subclass) -> None:
    """Test that supported_device_ids returns a dict mapping device IDs to names."""
    result = subclass.supported_device_ids
    assert isinstance(result, dict)

    for key, value in result.items():
        assert isinstance(key, tuple)
        for item in key:
            assert isinstance(item, int)
        assert isinstance(value, str)


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_vendor(subclass) -> None:
    """Test that vendor() returns a string identifying the vendor name."""
    result = subclass.vendor()
    assert isinstance(result, str)


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_unique_device_names(subclass) -> None:
    """Test that unique_device_names() returns a list of unique device name strings."""
    result = subclass.unique_device_names()
    assert isinstance(result, list)

    for item in result:
        assert isinstance(item, str)


@pytest.mark.parametrize(("subclass", "devices"), list(HardwareCatalog.items()))
def test_implementation_classmethod_claims(subclass, devices) -> None:
    """Test that claims() returns True for devices that the subclass should support."""
    for device in devices:
        result = subclass.claims(device)
        assert isinstance(result, bool)
        assert result is True


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_does_not_claim_bogus(
    subclass,
    hardware_devices,
) -> None:
    """Test that claims() returns False for unsupported devices."""
    for device in hardware_devices:
        result = subclass.claims(device)
        assert isinstance(result, bool)
        assert result is False


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_subclasses(subclass) -> None:
    """Test that subclasses() returns a list of subclasses that inherit from the subclass."""
    results = subclass.subclasses()
    assert isinstance(results, list)
    for item in results:
        assert issubclass(item, subclass)


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_supported_lights(subclass) -> None:
    """Test that supported_lights() returns a dict mapping vendor names to devices."""
    results = subclass.supported_lights()
    assert isinstance(results, dict)
    for key, value in results.items():
        assert isinstance(key, str)
        for item in value:
            assert isinstance(item, str)


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_available_hardware(subclass) -> None:
    """Test that available_hardware() returns a dict mapping subclasses to Hardware devices."""
    results = subclass.available_hardware()
    assert isinstance(results, dict)
    for subclasses, devices in results.items():
        assert issubclass(subclasses, subclass)
        assert isinstance(devices, list)
        for device in devices:
            assert isinstance(device, Hardware)


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_all_lights(subclass) -> None:
    """Test that all_lights() returns a list of all available light instances."""
    results = subclass.all_lights()
    assert isinstance(results, list)
    for item in results:
        assert isinstance(item, subclass)


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_all_lights_filtered_false(subclass) -> None:
    """Test that all_lights() with filters returns a list of matching light instances."""
    results = subclass.all_lights(
        reset=False, exclusive=False, predicate=lambda h: False
    )
    assert len(results) == 0


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_all_lights_filtered_true(subclass) -> None:
    """Test that all_lights() with filters returns a list of matching light instances."""
    results = subclass.all_lights(predicate=lambda h: True)
    assert len(results) >= 0


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_first_light(subclass) -> None:
    """Test that first_light() returns first available light or raises NoLightsFoundError."""
    try:
        result = subclass.first_light()
        assert isinstance(result, subclass)
    except NoLightsFoundError:
        pass


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_first_light_filtered_false(subclass) -> None:
    """Test first_light() with filters raises NoLightsFoundError when no match."""
    result = subclass.first_light(
        reset=False,
        exclusive=False,
        predicate=lambda h: True,
    )
    assert isinstance(result, subclass)


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_first_light_filtered_false(subclass) -> None:
    """Test first_light() with filters raises NoLightsFoundError when no match."""
    with pytest.raises(NoLightsFoundError):
        result = subclass.first_light(
            reset=False,
            exclusive=False,
            predicate=lambda h: False,
        )


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_at_path_dne(subclass) -> None:
    """Test that at_path() raises NoLightsFoundError for an invalid path."""
    with pytest.raises(NoLightsFoundError):
        result = subclass.at_path("Not A Path")


@pytest.mark.skip(reason="No valid hardware paths in test catalog.")
@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_classmethod_at_path_exists(subclass) -> None:
    """Test that at_path() returns a light instance for valid path."""
    result = subclass.at_path("/BOGUS/PATH")
    assert isinstance(result, subclass)
    assert result.hardware.path == b"/BOGUS/PATH"


@pytest.mark.parametrize("subclass", VENDOR_SUBCLASSES)
def test_implementation_init_with_bogus_hardware(subclass, hardware_devices) -> None:
    """Test that initializing with unsupported hardware raises HardwareUnsupportedError."""
    for device in hardware_devices:
        with pytest.raises(HardwareUnsupportedError):
            subclass(device, reset=False, exclusive=False)


@pytest.mark.parametrize(("subclass", "devices"), list(HardwareCatalog.items()))
def test_implementation_init(subclass, devices) -> None:
    """Test that light instances can be initialized with supported hardware and work."""
    for device in devices:
        ## EJO The aquire and release methods are monkey patched here to
        ##     to avoid really trying to acquire/release potentially bogus
        ##     hardware devices.  Additionally, the write and read strategy
        ##     methods are monkey patched to avoid any real I/O operations.

        device.acquire = lambda: None
        device.release = lambda: None

        class TestSubclass(subclass):
            def _write(self, buf: bytes) -> int:
                return len(buf)

            def _read(self, nbytes: int, timeout: int | None = None) -> bytes:
                return bytes(nbytes)

            @property
            def write_strategy(self) -> Callable[[bytes], int]:
                return self._write

            @property
            def read_strategy(self) -> Callable[[int, int | None], bytes]:
                return self._read

        result = TestSubclass(device, reset=False, exclusive=False)

        assert isinstance(result, subclass)

        assert isinstance(result.hardware, Hardware)
        assert result.hardware == device
        assert result.reset is False
        assert result.exclusive is False

        assert isinstance(result.sort_key, tuple)
        for item in result.sort_key:
            assert isinstance(item, str)

        assert isinstance(result.name, str)
        assert isinstance(result.hex, str)
        assert isinstance(result.read_strategy, Callable)
        assert isinstance(result.write_strategy, Callable)

        assert isinstance(bytes(result), bytes)

        assert isinstance(result.red, int)
        assert result.red == 0
        assert isinstance(result.green, int)
        assert result.green == 0
        assert isinstance(result.blue, int)
        assert result.blue == 0

        assert isinstance(result.color, tuple)
        assert all(c == 0 for c in result.color)

        color = (255, 255, 255)

        result.on(color)

        assert all(c == 0xFF for c in result.color)
        assert result.red == 0xFF
        assert result.green == 0xFF
        assert result.blue == 0xFF

        result.off()

        assert all(c == 0x00 for c in result.color)
        assert result.red == 0x00
        assert result.green == 0x00
        assert result.blue == 0x00


def test_vendor_base_class_hierarchies() -> None:
    """Test that all vendor devices inherit from their appropriate vendor base classes."""
    # Import all vendor base classes

    # Define expected vendor mappings
    vendor_hierarchies = {
        "Agile Innovative": AgileInnovativeBase,
        "CompuLab": CompuLabBase,
        "Embrava": EmbravaBase,
        "EPOS": EPOSBase,
        "Kuando": KuandoBase,
        "Luxafor": LuxaforBase,
        "MuteMe": MuteMeBase,
        "Plantronics": PlantronicsBase,
        "ThingM": ThingMBase,
    }

    # Test each vendor base class has correct vendor() method
    for expected_vendor, base_class in vendor_hierarchies.items():
        assert base_class.vendor() == expected_vendor

    # Test all device classes inherit from appropriate vendor bases
    for device_class in VENDOR_SUBCLASSES:
        vendor_name = device_class.vendor()
        expected_base = vendor_hierarchies.get(vendor_name)

        if expected_base:
            assert issubclass(device_class, expected_base), (
                f"{device_class.__name__} should inherit from {expected_base.__name__} "
                f"for vendor '{vendor_name}'"
            )

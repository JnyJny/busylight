"""Tests for vendor-specific Lights classes functionality."""

from typing import Any, ClassVar
from unittest.mock import Mock, patch

import pytest

from busylight_core import (
    AgileInnovativeLights,
    CompuLabLights,
    EmbravaLights,
    EPOSLights,
    KuandoLights,
    Light,
    LuxaforLights,
    MuteMeLights,
    NoLightsFoundError,
    PlantronicsLights,
    ThingMLights,
)
from busylight_core.hardware import Hardware
from busylight_core.vendors.agile_innovative.blinkstick_base import BlinkStickBase
from busylight_core.vendors.embrava.embrava_base import EmbravaBase
from busylight_core.vendors.kuando.busylight_base import BusylightBase
from busylight_core.vendors.luxafor.luxafor_base import LuxaforBase
from busylight_core.vendors.thingm.thingm_base import ThingMBase


class TestVendorLightsClasses:
    """Test vendor-specific Lights classes functionality."""

    @pytest.fixture
    def mock_hardware_devices(self) -> dict[str, Any]:
        """Create mock hardware devices with different vendor/product IDs."""
        embrava_hw = Mock(spec=Hardware)
        embrava_hw.vendor_id = 0x2C0D
        embrava_hw.product_id = 0x0001

        kuando_hw = Mock(spec=Hardware)
        kuando_hw.vendor_id = 0x27BB
        kuando_hw.product_id = 0x3BCA

        luxafor_hw = Mock(spec=Hardware)
        luxafor_hw.vendor_id = 0x04D8
        luxafor_hw.product_id = 0xF372

        thingm_hw = Mock(spec=Hardware)
        thingm_hw.vendor_id = 0x27B8
        thingm_hw.product_id = 0x01ED

        return {
            "embrava": embrava_hw,
            "kuando": kuando_hw,
            "luxafor": luxafor_hw,
            "thingm": thingm_hw,
        }

    def test_all_vendor_lights_classes_have_all_lights_method(self) -> None:
        """Test all vendor Lights classes have all_lights() method."""
        vendor_classes = [
            AgileInnovativeLights,
            CompuLabLights,
            EmbravaLights,
            EPOSLights,
            KuandoLights,
            LuxaforLights,
            MuteMeLights,
            PlantronicsLights,
            ThingMLights,
        ]

        for vendor_class in vendor_classes:
            assert hasattr(vendor_class, "all_lights")
            assert callable(vendor_class.all_lights)

    def test_all_vendor_lights_classes_have_first_light_method(self) -> None:
        """Test all vendor Lights classes have first_light() method."""
        vendor_classes = [
            AgileInnovativeLights,
            CompuLabLights,
            EmbravaLights,
            EPOSLights,
            KuandoLights,
            LuxaforLights,
            MuteMeLights,
            PlantronicsLights,
            ThingMLights,
        ]

        for vendor_class in vendor_classes:
            assert hasattr(vendor_class, "first_light")
            assert callable(vendor_class.first_light)

    def test_vendor_lights_inheritance_from_base_classes(self) -> None:
        """Test vendor Lights classes are aliases for base classes."""
        # EmbravaLights should be EmbravaBase
        assert EmbravaLights is EmbravaBase

        # KuandoLights should be BusylightBase (not KuandoBase)
        assert KuandoLights is BusylightBase

        # LuxaforLights should be LuxaforBase
        assert LuxaforLights is LuxaforBase

        # ThingMLights should be ThingMBase
        assert ThingMLights is ThingMBase

        # AgileInnovativeLights should be BlinkStickBase
        assert AgileInnovativeLights is BlinkStickBase

    def test_vendor_lights_classes_have_vendor_method(self) -> None:
        """Test vendor Lights classes have correct vendor() methods."""
        expected_vendors = {
            EmbravaLights: "Embrava",
            KuandoLights: "Kuando",
            LuxaforLights: "Luxafor",
            ThingMLights: "ThingM",
        }

        for vendor_class, expected_vendor in expected_vendors.items():
            assert vendor_class.vendor() == expected_vendor

    @patch("busylight_core.hardware.Hardware.enumerate")
    def test_embrava_lights_available_hardware_filters_correctly(
        self, mock_enumerate: Mock, mock_hardware_devices: dict[str, Any]
    ) -> None:
        """Test EmbravaLights.available_hardware() only returns Embrava devices."""

        # Mock concrete Embrava devices that would claim the hardware
        class MockBlynclight(EmbravaLights):
            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
                (0x2C0D, 0x0001): "Blynclight",
            }

            @classmethod
            def claims(cls, hardware: Hardware) -> bool:
                return (
                    hardware.vendor_id,
                    hardware.product_id,
                ) in cls.supported_device_ids

        # Mock the subclasses method to return our mock
        with patch.object(EmbravaLights, "subclasses", return_value=[MockBlynclight]):
            mock_enumerate.return_value = [
                mock_hardware_devices["embrava"],
                mock_hardware_devices["kuando"],
                mock_hardware_devices["luxafor"],
            ]

            available = EmbravaLights.available_hardware()

            # Should only contain Embrava devices
            assert len(available) == 1
            assert MockBlynclight in available
            assert len(available[MockBlynclight]) == 1

    @patch("busylight_core.hardware.Hardware.enumerate")
    def test_vendor_lights_available_hardware_empty_when_no_devices(
        self, mock_enumerate: Mock
    ) -> None:
        """Test vendor Lights classes return empty dict when no compatible devices."""
        mock_enumerate.return_value = []

        available = EmbravaLights.available_hardware()
        assert available == {}

    @patch.object(EmbravaLights, "available_hardware")
    def test_embrava_lights_all_lights_calls_vendor_available_hardware(
        self, mock_available_hardware: Mock
    ) -> None:
        """Test EmbravaLights.all_lights() uses vendor-specific available_hardware."""
        # Create mock device instances
        mock_device1 = Mock()

        # Create mock Light subclass
        mock_light_class = Mock()
        mock_light_class.return_value = mock_device1

        # Mock available_hardware to return vendor-specific results
        mock_available_hardware.return_value = {
            mock_light_class: [Mock(), Mock()]  # Two hardware devices
        }

        # This should create two light instances (but mock will return same instance)
        lights = EmbravaLights.all_lights()

        # Verify vendor-specific available_hardware was called
        mock_available_hardware.assert_called_once()

        # Should attempt to create lights from vendor hardware
        assert len(lights) == 2

    @patch.object(EmbravaLights, "available_hardware")
    def test_embrava_lights_first_light_calls_vendor_available_hardware(
        self, mock_available_hardware: Mock
    ) -> None:
        """Test EmbravaLights.first_light() uses vendor-specific available_hardware."""
        # Create mock device instance
        mock_device = Mock()

        # Create mock Light subclass
        mock_light_class = Mock()
        mock_light_class.return_value = mock_device

        # Mock available_hardware to return vendor-specific results
        mock_available_hardware.return_value = {
            mock_light_class: [Mock()]  # One hardware device
        }

        light = EmbravaLights.first_light()

        # Verify vendor-specific available_hardware was called
        mock_available_hardware.assert_called_once()

        # Should return the created light instance
        assert light == mock_device

    @patch.object(EmbravaLights, "available_hardware")
    def test_vendor_lights_first_light_raises_no_lights_found_when_empty(
        self, mock_available_hardware: Mock
    ) -> None:
        """Test vendor Lights classes raise NoLightsFoundError when no devices available."""
        # Mock empty available hardware
        mock_available_hardware.return_value = {}

        with pytest.raises(NoLightsFoundError):
            EmbravaLights.first_light()

    @patch.object(Light, "available_hardware")
    def test_backward_compatibility_light_all_lights_unchanged(
        self, mock_available_hardware: Mock
    ) -> None:
        """Test Light.all_lights() still returns all devices from all vendors."""
        # Create mock devices from different vendors
        embrava_device = Mock()
        kuando_device = Mock()

        # Create mock Light subclasses
        embrava_class = Mock()
        embrava_class.return_value = embrava_device

        kuando_class = Mock()
        kuando_class.return_value = kuando_device

        # Mock available_hardware to return devices from multiple vendors
        mock_available_hardware.return_value = {
            embrava_class: [Mock()],  # One Embrava device
            kuando_class: [Mock()],  # One Kuando device
        }

        lights = Light.all_lights()

        # Should return devices from all vendors
        assert len(lights) == 2
        assert embrava_device in lights
        assert kuando_device in lights

    @patch.object(Light, "available_hardware")
    def test_backward_compatibility_light_first_light_unchanged(
        self, mock_available_hardware: Mock
    ) -> None:
        """Test Light.first_light() still works as before."""
        # Create mock device
        mock_device = Mock()

        # Create mock Light subclass
        mock_light_class = Mock()
        mock_light_class.return_value = mock_device

        # Mock available_hardware to return a device
        mock_available_hardware.return_value = {
            mock_light_class: [Mock()]  # One hardware device
        }

        first_light = Light.first_light()

        # Should return the first available device regardless of vendor
        assert first_light == mock_device

    def test_vendor_lights_classes_are_importable_from_main_module(self) -> None:
        """Test vendor Lights classes can be imported from main busylight_core module."""
        # Verify they are all classes (already imported at module level)
        vendor_classes = [
            AgileInnovativeLights,
            CompuLabLights,
            EmbravaLights,
            EPOSLights,
            KuandoLights,
            LuxaforLights,
            MuteMeLights,
            PlantronicsLights,
            ThingMLights,
        ]

        for vendor_class in vendor_classes:
            assert isinstance(vendor_class, type)
            # They should all be subclasses of Light
            assert issubclass(vendor_class, Light)

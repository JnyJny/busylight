"""Tests for Plantronics Status Indicator implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.embrava.blynclight import Blynclight
from busylight_core.vendors.embrava.blynclight_plus import BlynclightPlus
from busylight_core.vendors.embrava.embrava_base import EmbravaBase
from busylight_core.vendors.embrava.implementation import FlashSpeed
from busylight_core.vendors.plantronics import StatusIndicator
from busylight_core.vendors.plantronics.plantronics_base import PlantronicsBase


class TestPlantronicsStatusIndicator:
    """Test the Plantronics Status Indicator device functionality."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for testing Status Indicator device."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x047F
        hardware.product_id = 0xD005
        hardware.device_id = (0x047F, 0xD005)
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def status_indicator(self, mock_hardware) -> StatusIndicator:
        """Create a StatusIndicator instance for testing."""
        # Mock the hardware handle methods
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=9)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 9)

        return StatusIndicator(mock_hardware, reset=False, exclusive=False)

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected Status Indicator device."""
        device_ids = StatusIndicator.supported_device_ids
        assert (0x047F, 0xD005) in device_ids
        assert device_ids[(0x047F, 0xD005)] == "Status Indicator"
        # Should only have one device ID for Plantronics
        assert len(device_ids) == 1

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        # Should inherit the vendor method from Blynclight base class
        # which gets vendor from module path (plantronics)
        assert StatusIndicator.vendor() == "Plantronics"

    def test_claims_method_with_status_indicator_hardware(self, mock_hardware) -> None:
        """Test claims() method with Status Indicator hardware."""
        # Test with correct Status Indicator device ID
        mock_hardware.device_id = (0x047F, 0xD005)
        assert StatusIndicator.claims(mock_hardware) is True

        # Test with Embrava Blynclight device ID (should not claim)
        mock_hardware.device_id = (0x2C0D, 0x0001)
        assert StatusIndicator.claims(mock_hardware) is False

        # Test with unknown device ID
        mock_hardware.device_id = (0x1234, 0x5678)
        assert StatusIndicator.claims(mock_hardware) is False

    def test_inheritance_from_blynclight(self, status_indicator) -> None:
        """Test that StatusIndicator properly inherits from EmbravaBase."""
        # Should be an instance of both StatusIndicator and EmbravaBase
        assert isinstance(status_indicator, StatusIndicator)

        assert isinstance(status_indicator, EmbravaBase)

        # Should have all Blynclight methods
        assert hasattr(status_indicator, "on")
        assert hasattr(status_indicator, "off")
        assert hasattr(status_indicator, "color")
        assert hasattr(status_indicator, "dim")
        assert hasattr(status_indicator, "bright")
        assert hasattr(status_indicator, "play_sound")
        assert hasattr(status_indicator, "stop_sound")
        assert hasattr(status_indicator, "mute")
        assert hasattr(status_indicator, "unmute")
        assert hasattr(status_indicator, "flash")
        assert hasattr(status_indicator, "stop_flashing")
        assert hasattr(status_indicator, "reset")

    def test_color_property_inherited(self, status_indicator) -> None:
        """Test color property inherited from Blynclight."""
        # Test setting color
        test_color = (255, 128, 64)
        status_indicator.color = test_color
        assert status_indicator.color == test_color

        # Test that it uses the state object from Blynclight
        assert status_indicator.state.red == 255
        assert status_indicator.state.green == 128
        assert status_indicator.state.blue == 64

    def test_on_method_inherited(self, status_indicator) -> None:
        """Test on() method inherited from Blynclight."""
        color = (200, 150, 100)
        status_indicator.on(color)
        assert status_indicator.color == color

    def test_dim_and_bright_methods_inherited(self, status_indicator) -> None:
        """Test dim() and bright() methods inherited from Blynclight."""
        # First turn on the device with some color
        status_indicator.on((100, 100, 100))

        # Test dim functionality
        status_indicator.dim()
        assert status_indicator.state.dim == 1

        # Test bright functionality
        status_indicator.bright()
        assert status_indicator.state.dim == 0

    def test_sound_methods_inherited(self, status_indicator) -> None:
        """Test sound-related methods inherited from Blynclight."""
        # Test play_sound
        status_indicator.play_sound(music=2, volume=3, repeat=True)
        assert status_indicator.state.play == 1
        assert status_indicator.state.music == 2
        assert status_indicator.state.volume == 3
        assert status_indicator.state.repeat == 1
        assert status_indicator.state.mute == 0

        # Test stop_sound
        status_indicator.stop_sound()
        assert status_indicator.state.play == 0

        # Test mute
        status_indicator.mute()
        assert status_indicator.state.mute == 1

        # Test unmute
        status_indicator.unmute()
        assert status_indicator.state.mute == 0

    def test_flash_methods_inherited(self, status_indicator) -> None:
        """Test flash-related methods inherited from Blynclight."""
        color = (255, 0, 0)

        # Test flash with default speed
        status_indicator.flash(color)
        assert status_indicator.color == color
        assert status_indicator.state.flash == 1
        assert status_indicator.state.speed == FlashSpeed.slow.value

        # Test flash with custom speed
        status_indicator.flash(color, FlashSpeed.fast)
        assert status_indicator.state.speed == FlashSpeed.fast.value

        # Test stop_flashing
        status_indicator.stop_flashing()
        assert status_indicator.state.flash == 0

    def test_bytes_method_inherited(self, status_indicator) -> None:
        """Test __bytes__ method inherited from Blynclight."""
        # Set a color and test the byte output format
        status_indicator.color = (128, 64, 192)
        result = bytes(status_indicator)

        # Should follow Blynclight format: [0, state_bytes..., 0xFF, 0x22]
        assert isinstance(result, bytes)
        assert len(result) == 9  # 1 + 6 state bytes + 1 + 1
        assert result[0] == 0
        assert result[-2] == 0xFF
        assert result[-1] == 0x22

    def test_bytes_method_when_off(self, status_indicator) -> None:
        """Test __bytes__ method when device is off."""
        # Turn off the device
        status_indicator.off((0, 0, 0))

        # Should set off, disable flash and dim when not lit
        assert status_indicator.state.off == 1
        assert status_indicator.state.flash == 0
        assert status_indicator.state.dim == 0

    def test_reset_method_inherited(self, status_indicator) -> None:
        """Test reset() method inherited from Blynclight."""
        # Set some state
        status_indicator.color = (255, 255, 255)
        status_indicator.flash((255, 0, 0))
        status_indicator.play_sound(music=3, volume=2)
        status_indicator.dim()

        # Reset should clear all state
        with patch.object(status_indicator, "update") as mock_update:
            status_indicator.reset()
            mock_update.assert_called_once()

    def test_device_specific_identification(self, status_indicator) -> None:
        """Test device-specific identification vs base Blynclight."""
        # Status Indicator should have different device IDs than base Blynclight
        blynclight_ids = Blynclight.supported_device_ids
        status_indicator_ids = StatusIndicator.supported_device_ids

        # Should not share any device IDs
        assert not set(blynclight_ids.keys()) & set(status_indicator_ids.keys())

        # Should be identified correctly
        assert status_indicator.name == "Status Indicator"

    def test_plantronics_vs_embrava_claiming(self, mock_hardware) -> None:
        """Test that Plantronics and Embrava devices don't cross-claim."""
        # Plantronics device should only be claimed by StatusIndicator
        mock_hardware.device_id = (0x047F, 0xD005)
        assert StatusIndicator.claims(mock_hardware) is True
        assert Blynclight.claims(mock_hardware) is False

        # Embrava device should only be claimed by Blynclight
        mock_hardware.device_id = (0x2C0D, 0x0001)
        assert StatusIndicator.claims(mock_hardware) is False
        assert Blynclight.claims(mock_hardware) is True

    def test_state_object_functionality(self, status_indicator) -> None:
        """Test that the state object works correctly."""
        # Should have a state object from Blynclight
        assert hasattr(status_indicator, "state")
        state = status_indicator.state

        # State should have all expected attributes
        assert hasattr(state, "red")
        assert hasattr(state, "green")
        assert hasattr(state, "blue")
        assert hasattr(state, "flash")
        assert hasattr(state, "dim")
        assert hasattr(state, "off")
        assert hasattr(state, "play")
        assert hasattr(state, "music")
        assert hasattr(state, "volume")
        assert hasattr(state, "repeat")
        assert hasattr(state, "mute")
        assert hasattr(state, "speed")

    def test_all_blynclight_features_available(self, status_indicator) -> None:
        """Test that all Blynclight features are available on Status Indicator."""
        # Color control
        status_indicator.on((255, 128, 64))
        assert status_indicator.is_lit

        # Brightness control
        status_indicator.dim()
        status_indicator.bright()

        # Sound control
        status_indicator.play_sound(music=1, volume=2, repeat=False)
        status_indicator.stop_sound()
        status_indicator.mute()
        status_indicator.unmute()

        # Flash control
        status_indicator.flash((255, 0, 0), FlashSpeed.fast)
        status_indicator.stop_flashing()

        # Device should handle all operations without errors
        assert True  # If we get here, all operations succeeded

    def test_batch_update_inherited(self, status_indicator) -> None:
        """Test that batch_update functionality is inherited."""
        # batch_update should be available from Light base class
        assert hasattr(status_indicator, "batch_update")

        # Test that operations use batch_update (inherited behavior)
        with patch.object(status_indicator, "update") as mock_update:
            status_indicator.on((255, 128, 64))
            # Should call update due to batch_update context
            mock_update.assert_called()

    def test_class_hierarchy(self) -> None:
        """Test the class hierarchy is correct."""
        # StatusIndicator should inherit from PlantronicsBase which inherits from BlynclightPlus

        assert issubclass(StatusIndicator, PlantronicsBase)
        assert issubclass(StatusIndicator, BlynclightPlus)
        assert issubclass(StatusIndicator, EmbravaBase)

        # Should have the expected method resolution order
        status_mro = StatusIndicator.__mro__

        # StatusIndicator -> PlantronicsBase -> BlynclightPlus -> EmbravaBase -> Light -> ...
        assert status_mro[0] == StatusIndicator
        assert status_mro[1] == PlantronicsBase
        assert status_mro[2] == BlynclightPlus

    def test_module_path_vendor_detection(self) -> None:
        """Test that vendor detection works via module path."""
        # The vendor method should extract 'plantronics' from the module path
        # StatusIndicator is in busylight_core.vendors.plantronics.status_indicator
        vendor = StatusIndicator.vendor()
        assert vendor == "Plantronics"

"""Tests for Luxafor Flag implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.light import Light
from busylight_core.vendors.luxafor import Bluetooth, BusyTag, Flag, Mute, Orb
from busylight_core.vendors.luxafor.implementation import Command, State
from busylight_core.vendors.luxafor.luxafor_base import LuxaforBase


class TestLuxaforFlag:
    """Test the Flag class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for testing."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x04D8
        hardware.product_id = 0xF372
        hardware.device_id = (0x04D8, 0xF372)
        hardware.connection_type = ConnectionType.HID
        hardware.product_string = "Luxafor Flag"
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def flag(self, mock_hardware) -> Flag:
        """Create a Flag instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=8)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 8)
        return Flag(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert Flag.vendor() == "Luxafor"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = Flag.supported_device_ids
        assert (0x04D8, 0xF372) in device_ids
        assert device_ids[(0x04D8, 0xF372)] == "Flag"

    def test_claims_method_with_keyerror(self, mock_hardware) -> None:
        """Test claims() method with KeyError in product_string processing."""
        # Create a mock that raises KeyError when split() is called
        mock_product_string = Mock()
        mock_product_string.split.side_effect = KeyError("test error")
        mock_hardware.product_string = mock_product_string

        # Mock super().claims() to return True (need to patch Light.claims)

        with (
            patch.object(Light, "claims", return_value=True),
            patch("busylight_core.vendors.luxafor.luxafor_base.logger") as mock_logger,
        ):
            result = Flag.claims(mock_hardware)

            assert result is False
            mock_logger.debug.assert_called_once()
            assert "problem" in str(mock_logger.debug.call_args)
            assert "test error" in str(mock_logger.debug.call_args)

    def test_claims_method_with_indexerror(self, mock_hardware) -> None:
        """Test claims() method with IndexError in product_string processing."""
        # Empty string will cause IndexError when split()[-1] is accessed
        mock_hardware.product_string = ""

        # Mock super().claims() to return True (need to patch Light.claims)

        with (
            patch.object(Light, "claims", return_value=True),
            patch("busylight_core.vendors.luxafor.luxafor_base.logger") as mock_logger,
        ):
            result = Flag.claims(mock_hardware)

            assert result is False
            mock_logger.debug.assert_called_once()
            assert "problem" in str(mock_logger.debug.call_args)
            assert "list index out of range" in str(mock_logger.debug.call_args)

    def test_claims_method_with_no_super_claim(self, mock_hardware) -> None:
        """Test claims() method when super().claims() returns False."""
        mock_hardware.product_string = "Luxafor Flag"

        # Mock super().claims() to return False
        with patch.object(Flag.__bases__[0], "claims", return_value=False):
            result = Flag.claims(mock_hardware)
            assert result is False

    def test_vendor_hierarchy(self, flag) -> None:
        """Test Flag inherits from LuxaforBase properly."""
        # Test inheritance hierarchy
        assert isinstance(flag, Flag)
        assert isinstance(flag, LuxaforBase)

        # Test class hierarchy
        assert issubclass(Flag, LuxaforBase)

        # Test vendor method comes from LuxaforBase
        assert Flag.vendor() == "Luxafor"
        assert LuxaforBase.vendor() == "Luxafor"


class TestLuxaforFlagState:
    """Test the Flag State class."""

    def test_state_bytes_with_fade_command(self) -> None:
        """Test State.__bytes__() with Fade command."""
        state = State()
        state.command = Command.Fade
        state.leds = 1
        state.color = (255, 128, 64)
        state.fade = 10
        state.repeat = 5

        result = bytes(state)
        expected = bytes([Command.Fade, 1, 255, 128, 64, 10, 5])
        assert result == expected

    def test_state_bytes_with_unsupported_command(self) -> None:
        """Test State.__bytes__() with unsupported command raises ValueError."""
        state = State()
        # Use a command value that's not Color or Fade
        state.command = 99  # Invalid command
        state.leds = 1
        state.color = (255, 128, 64)

        with patch(
            "busylight_core.vendors.luxafor.implementation.state.logger"
        ) as mock_logger:
            with pytest.raises(ValueError, match="Unsupported command: 99"):
                bytes(state)

            # Should log the error before raising
            mock_logger.debug.assert_called_once_with("Unsupported command: 99")

    def test_state_bytes_with_unknown_command_enum(self) -> None:
        """Test State.__bytes__() with unknown command enum."""
        state = State()
        # Create a mock command that's not in the match statement
        mock_command = Mock()
        mock_command.__class__ = Command
        state.command = mock_command
        state.leds = 1
        state.color = (255, 128, 64)

        with patch(
            "busylight_core.vendors.luxafor.implementation.state.logger"
        ) as mock_logger:
            with pytest.raises(
                ValueError, match=f"Unsupported command: {mock_command}"
            ):
                bytes(state)

            # Should log the error before raising
            mock_logger.debug.assert_called_once_with(
                f"Unsupported command: {mock_command}"
            )

    def test_method_resolution_order(self) -> None:
        """Test MRO follows expected pattern."""
        mro = Flag.__mro__

        # Should be: Flag -> LuxaforBase -> Light -> ...
        assert mro[0] == Flag
        assert mro[1].__name__ == "LuxaforBase"
        assert mro[2].__name__ == "Light"

    def test_luxafor_devices_inherit_from_base(self) -> None:
        """Test all Luxafor devices inherit from LuxaforBase."""
        luxafor_devices = [Flag, Bluetooth, BusyTag, Mute, Orb]

        for device_class in luxafor_devices:
            assert issubclass(device_class, LuxaforBase)
            assert device_class.vendor() == "Luxafor"

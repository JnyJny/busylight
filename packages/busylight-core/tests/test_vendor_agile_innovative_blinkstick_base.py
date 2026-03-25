"""Tests for Agile Innovative BlinkStick (base model) implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.agile_innovative import BlinkStick
from busylight_core.vendors.agile_innovative.agile_innovative_base import (
    AgileInnovativeBase,
)
from busylight_core.vendors.agile_innovative.blinkstick_base import (
    BlinkStickBase,
)
from busylight_core.vendors.agile_innovative.implementation import State


class TestBlinkStick:
    """Test the BlinkStick class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for BlinkStick."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x20A0
        hardware.product_id = 0x41E5
        hardware.device_id = (0x20A0, 0x41E5)
        hardware.serial_number = "BS123456-1.0"
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def blinkstick(self, mock_hardware) -> BlinkStick:
        """Create a BlinkStick instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=4)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 4)
        return BlinkStick(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert BlinkStick.vendor() == "Agile Innovative"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = BlinkStick.supported_device_ids
        assert (0x20A0, 0x41E5) in device_ids
        assert device_ids[(0x20A0, 0x41E5)] == "BlinkStick"

    def test_claims_method_valid_hardware(self, mock_hardware) -> None:
        """Test claims() method with valid hardware."""
        mock_hardware.serial_number = "BS123456-1.0"

        with patch.object(BlinkStick.__bases__[0], "claims", return_value=True):
            assert BlinkStick.claims(mock_hardware) is True

    def test_claims_method_invalid_serial_number(self, mock_hardware) -> None:
        """Test claims() method with invalid serial number."""
        mock_hardware.serial_number = "BS123456-2.0"  # Wrong major version

        with patch.object(BlinkStick.__bases__[0], "claims", return_value=True):
            assert BlinkStick.claims(mock_hardware) is False

    def test_claims_method_invalid_serial_format(self, mock_hardware) -> None:
        """Test claims() method with invalid serial format."""
        mock_hardware.serial_number = "12345"  # Invalid format

        with patch.object(BlinkStick.__bases__[0], "claims", return_value=True):
            assert BlinkStick.claims(mock_hardware) is False

    def test_claims_method_super_false(self, mock_hardware) -> None:
        """Test claims() method when super().claims() returns False."""
        mock_hardware.serial_number = "BS123456-1.0"

        with patch.object(BlinkStick.__bases__[0], "claims", return_value=False):
            assert BlinkStick.claims(mock_hardware) is False

    def test_state_property(self, blinkstick) -> None:
        """Test state property returns BlinkStick state."""
        state = blinkstick.state
        assert isinstance(state, State)
        assert state.report == 1
        assert state.nleds == 1
        # Should be cached
        assert blinkstick.state is state

    def test_bytes_method(self, blinkstick) -> None:
        """Test __bytes__ method returns state bytes."""
        state_bytes = bytes(blinkstick)
        expected_bytes = bytes(blinkstick.state)
        assert state_bytes == expected_bytes

    def test_on_method_all_leds(self, blinkstick) -> None:
        """Test on() method with LED=0 (all LEDs)."""
        color = (255, 128, 64)
        with patch.object(blinkstick, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick.on(color, led=0)

            assert blinkstick.color == color
            assert blinkstick.state.color == color
            mock_batch.assert_called_once()

    def test_on_method_specific_led(self, blinkstick) -> None:
        """Test on() method with specific LED."""
        color = (200, 100, 50)
        led = 1

        with patch.object(blinkstick, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick.on(color, led=led)

            assert blinkstick.color == color
            # For single LED device, individual LED should be set
            assert blinkstick.state.get_led(0) == color
            mock_batch.assert_called_once()

    def test_vendor_hierarchy(self, blinkstick) -> None:
        """Test BlinkStick inherits from AgileInnovativeBase properly."""
        # Test inheritance hierarchy
        assert isinstance(blinkstick, BlinkStick)
        assert isinstance(blinkstick, BlinkStickBase)
        assert isinstance(blinkstick, AgileInnovativeBase)

        # Test class hierarchy
        assert issubclass(BlinkStick, BlinkStickBase)
        assert issubclass(BlinkStick, AgileInnovativeBase)
        assert issubclass(BlinkStickBase, AgileInnovativeBase)

        # Test vendor method comes from AgileInnovativeBase
        assert BlinkStick.vendor() == "Agile Innovative"
        assert BlinkStickBase.vendor() == "Agile Innovative"
        assert AgileInnovativeBase.vendor() == "Agile Innovative"

    def test_method_resolution_order(self) -> None:
        """Test MRO follows expected pattern."""
        mro = BlinkStick.__mro__

        # Should be: BlinkStick -> BlinkStickBase -> AgileInnovativeBase -> Light -> ...
        assert mro[0] == BlinkStick
        assert mro[1].__name__ == "BlinkStickBase"
        assert mro[2].__name__ == "AgileInnovativeBase"
        assert mro[3].__name__ == "Light"

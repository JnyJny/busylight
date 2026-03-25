"""Tests for Agile Innovative BlinkStick Flex implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.agile_innovative import BlinkStickFlex
from busylight_core.vendors.agile_innovative.implementation import State


class TestBlinkStickFlex:
    """Test the BlinkStickFlex class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for BlinkStick Flex."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x20A0
        hardware.product_id = 0x41E5
        hardware.device_id = (0x20A0, 0x41E5)
        hardware.serial_number = "BS123456-3.0"
        hardware.release_number = 0x203
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def blinkstick_flex(self, mock_hardware) -> BlinkStickFlex:
        """Create a BlinkStickFlex instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=98)  # 2 + 32*3
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 98)
        return BlinkStickFlex(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert BlinkStickFlex.vendor() == "Agile Innovative"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = BlinkStickFlex.supported_device_ids
        assert (0x20A0, 0x41E5) in device_ids
        assert device_ids[(0x20A0, 0x41E5)] == "BlinkStick Flex"

    def test_claims_method_valid_hardware(self, mock_hardware) -> None:
        """Test claims() method with valid hardware."""
        mock_hardware.serial_number = "BS123456-3.0"
        mock_hardware.release_number = 0x203

        with patch.object(BlinkStickFlex.__bases__[0], "claims", return_value=True):
            assert BlinkStickFlex.claims(mock_hardware) is True

    def test_claims_method_invalid_release_number(self, mock_hardware) -> None:
        """Test claims() method with invalid release number."""
        mock_hardware.serial_number = "BS123456-3.0"
        mock_hardware.release_number = 0x201  # Wrong release number

        with patch.object(BlinkStickFlex.__bases__[0], "claims", return_value=True):
            assert BlinkStickFlex.claims(mock_hardware) is False

    def test_claims_method_invalid_major_version(self, mock_hardware) -> None:
        """Test claims() method with invalid major version."""
        mock_hardware.serial_number = "BS123456-2.0"  # Wrong major version
        mock_hardware.release_number = 0x203

        with patch.object(BlinkStickFlex.__bases__[0], "claims", return_value=True):
            assert BlinkStickFlex.claims(mock_hardware) is False

    def test_claims_method_invalid_serial_format(self, mock_hardware) -> None:
        """Test claims() method with invalid serial format."""
        mock_hardware.serial_number = "12345"  # Invalid format
        mock_hardware.release_number = 0x203

        with patch.object(BlinkStickFlex.__bases__[0], "claims", return_value=True):
            assert BlinkStickFlex.claims(mock_hardware) is False

    def test_claims_method_super_false(self, mock_hardware) -> None:
        """Test claims() method when super().claims() returns False."""
        mock_hardware.serial_number = "BS123456-3.0"
        mock_hardware.release_number = 0x203

        with patch.object(BlinkStickFlex.__bases__[0], "claims", return_value=False):
            assert BlinkStickFlex.claims(mock_hardware) is False

    def test_state_property(self, blinkstick_flex) -> None:
        """Test state property returns BlinkStick Flex state."""
        state = blinkstick_flex.state
        assert isinstance(state, State)
        assert state.report == 6
        assert state.nleds == 32
        # Should be cached
        assert blinkstick_flex.state is state

    def test_bytes_method(self, blinkstick_flex) -> None:
        """Test __bytes__ method returns state bytes."""
        state_bytes = bytes(blinkstick_flex)
        expected_bytes = bytes(blinkstick_flex.state)
        assert state_bytes == expected_bytes

    def test_on_method_all_leds(self, blinkstick_flex) -> None:
        """Test on() method with LED=0 (all LEDs)."""
        color = (255, 128, 64)
        with patch.object(blinkstick_flex, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick_flex.on(color, led=0)

            assert blinkstick_flex.color == color
            assert blinkstick_flex.state.color == color
            mock_batch.assert_called_once()

    def test_on_method_specific_led(self, blinkstick_flex) -> None:
        """Test on() method with specific LED."""
        color = (200, 100, 50)
        led = 16

        with patch.object(blinkstick_flex, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick_flex.on(color, led=led)

            assert blinkstick_flex.color == color
            # Check that the specific LED was set
            assert blinkstick_flex.state.get_led(led - 1) == color
            mock_batch.assert_called_once()

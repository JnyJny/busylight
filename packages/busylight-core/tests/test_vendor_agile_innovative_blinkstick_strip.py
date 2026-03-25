"""Tests for Agile Innovative BlinkStick Strip implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.agile_innovative import BlinkStickStrip
from busylight_core.vendors.agile_innovative.implementation import State


class TestBlinkStickStrip:
    """Test the BlinkStickStrip class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for BlinkStick Strip."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x20A0
        hardware.product_id = 0x41E5
        hardware.device_id = (0x20A0, 0x41E5)
        hardware.serial_number = "BS123456-3.0"
        hardware.release_number = 0x201
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def blinkstick_strip(self, mock_hardware) -> BlinkStickStrip:
        """Create a BlinkStickStrip instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=26)  # 2 + 8*3
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 26)
        return BlinkStickStrip(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert BlinkStickStrip.vendor() == "Agile Innovative"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = BlinkStickStrip.supported_device_ids
        assert (0x20A0, 0x41E5) in device_ids
        assert device_ids[(0x20A0, 0x41E5)] == "BlinkStick Strip"

    def test_claims_method_valid_hardware(self, mock_hardware) -> None:
        """Test claims() method with valid hardware."""
        mock_hardware.serial_number = "BS123456-3.0"
        mock_hardware.release_number = 0x201

        with patch.object(BlinkStickStrip.__bases__[0], "claims", return_value=True):
            assert BlinkStickStrip.claims(mock_hardware) is True

    def test_claims_method_invalid_release_number(self, mock_hardware) -> None:
        """Test claims() method with invalid release number."""
        mock_hardware.serial_number = "BS123456-3.0"
        mock_hardware.release_number = 0x202  # Wrong release number

        with patch.object(BlinkStickStrip.__bases__[0], "claims", return_value=True):
            assert BlinkStickStrip.claims(mock_hardware) is False

    def test_claims_method_invalid_major_version(self, mock_hardware) -> None:
        """Test claims() method with invalid major version."""
        mock_hardware.serial_number = "BS123456-2.0"  # Wrong major version
        mock_hardware.release_number = 0x201

        with patch.object(BlinkStickStrip.__bases__[0], "claims", return_value=True):
            assert BlinkStickStrip.claims(mock_hardware) is False

    def test_claims_method_invalid_serial_format(self, mock_hardware) -> None:
        """Test claims() method with invalid serial format."""
        mock_hardware.serial_number = "12345"  # Invalid format
        mock_hardware.release_number = 0x201

        with patch.object(BlinkStickStrip.__bases__[0], "claims", return_value=True):
            assert BlinkStickStrip.claims(mock_hardware) is False

    def test_claims_method_super_false(self, mock_hardware) -> None:
        """Test claims() method when super().claims() returns False."""
        mock_hardware.serial_number = "BS123456-3.0"
        mock_hardware.release_number = 0x201

        with patch.object(BlinkStickStrip.__bases__[0], "claims", return_value=False):
            assert BlinkStickStrip.claims(mock_hardware) is False

    def test_state_property(self, blinkstick_strip) -> None:
        """Test state property returns BlinkStick Strip state."""
        state = blinkstick_strip.state
        assert isinstance(state, State)
        assert state.report == 6
        assert state.nleds == 8
        # Should be cached
        assert blinkstick_strip.state is state

    def test_bytes_method(self, blinkstick_strip) -> None:
        """Test __bytes__ method returns state bytes."""
        state_bytes = bytes(blinkstick_strip)
        expected_bytes = bytes(blinkstick_strip.state)
        assert state_bytes == expected_bytes

    def test_on_method_all_leds(self, blinkstick_strip) -> None:
        """Test on() method with LED=0 (all LEDs)."""
        color = (255, 128, 64)
        with patch.object(blinkstick_strip, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick_strip.on(color, led=0)

            assert blinkstick_strip.color == color
            assert blinkstick_strip.state.color == color
            mock_batch.assert_called_once()

    def test_on_method_specific_led(self, blinkstick_strip) -> None:
        """Test on() method with specific LED."""
        color = (200, 100, 50)
        led = 5

        with patch.object(blinkstick_strip, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick_strip.on(color, led=led)

            assert blinkstick_strip.color == color
            # Check that the specific LED was set
            assert blinkstick_strip.state.get_led(led - 1) == color
            mock_batch.assert_called_once()

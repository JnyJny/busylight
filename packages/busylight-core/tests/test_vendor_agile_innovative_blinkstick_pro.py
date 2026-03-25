"""Tests for Agile Innovative BlinkStick Pro implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.agile_innovative import BlinkStickPro
from busylight_core.vendors.agile_innovative.implementation import State


class TestBlinkStickPro:
    """Test the BlinkStickPro class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for BlinkStick Pro."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x20A0
        hardware.product_id = 0x41E5
        hardware.device_id = (0x20A0, 0x41E5)
        hardware.serial_number = "BS123456-2.0"
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def blinkstick_pro(self, mock_hardware) -> BlinkStickPro:
        """Create a BlinkStickPro instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=578)  # 2 + 192*3
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 578)
        return BlinkStickPro(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert BlinkStickPro.vendor() == "Agile Innovative"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = BlinkStickPro.supported_device_ids
        assert (0x20A0, 0x41E5) in device_ids
        assert device_ids[(0x20A0, 0x41E5)] == "BlinkStick Pro"

    def test_claims_method_valid_hardware(self, mock_hardware) -> None:
        """Test claims() method with valid hardware."""
        mock_hardware.serial_number = "BS123456-2.0"

        with patch.object(BlinkStickPro.__bases__[0], "claims", return_value=True):
            assert BlinkStickPro.claims(mock_hardware) is True

    def test_claims_method_invalid_serial_number(self, mock_hardware) -> None:
        """Test claims() method with invalid serial number."""
        mock_hardware.serial_number = "BS123456-1.0"  # Wrong major version

        with patch.object(BlinkStickPro.__bases__[0], "claims", return_value=True):
            assert BlinkStickPro.claims(mock_hardware) is False

    def test_claims_method_invalid_serial_format(self, mock_hardware) -> None:
        """Test claims() method with invalid serial format."""
        mock_hardware.serial_number = "12345"  # Invalid format

        with patch.object(BlinkStickPro.__bases__[0], "claims", return_value=True):
            assert BlinkStickPro.claims(mock_hardware) is False

    def test_claims_method_super_false(self, mock_hardware) -> None:
        """Test claims() method when super().claims() returns False."""
        mock_hardware.serial_number = "BS123456-2.0"

        with patch.object(BlinkStickPro.__bases__[0], "claims", return_value=False):
            assert BlinkStickPro.claims(mock_hardware) is False

    def test_state_property(self, blinkstick_pro) -> None:
        """Test state property returns BlinkStick Pro state."""
        state = blinkstick_pro.state
        assert isinstance(state, State)
        assert state.report == 2
        assert state.nleds == 192
        # Should be cached
        assert blinkstick_pro.state is state

    def test_bytes_method(self, blinkstick_pro) -> None:
        """Test __bytes__ method returns state bytes."""
        state_bytes = bytes(blinkstick_pro)
        expected_bytes = bytes(blinkstick_pro.state)
        assert state_bytes == expected_bytes

    def test_on_method_all_leds(self, blinkstick_pro) -> None:
        """Test on() method with LED=0 (all LEDs)."""
        color = (255, 128, 64)
        with patch.object(blinkstick_pro, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick_pro.on(color, led=0)

            assert blinkstick_pro.color == color
            assert blinkstick_pro.state.color == color
            mock_batch.assert_called_once()

    def test_on_method_specific_led(self, blinkstick_pro) -> None:
        """Test on() method with specific LED."""
        color = (200, 100, 50)
        led = 50

        with patch.object(blinkstick_pro, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick_pro.on(color, led=led)

            assert blinkstick_pro.color == color
            # Check that the specific LED was set
            assert blinkstick_pro.state.get_led(led - 1) == color
            mock_batch.assert_called_once()

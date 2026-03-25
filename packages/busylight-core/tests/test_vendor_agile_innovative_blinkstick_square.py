"""Tests for Agile Innovative BlinkStick Square implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.agile_innovative import BlinkStickSquare
from busylight_core.vendors.agile_innovative.implementation import State


class TestBlinkStickSquare:
    """Test the BlinkStickSquare class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for BlinkStick Square"""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x20A0
        hardware.product_id = 0x41E5
        hardware.device_id = (0x20A0, 0x41E5)
        hardware.serial_number = "BS123456-3.0"
        hardware.release_number = 0x200
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def blinkstick_square(self, mock_hardware) -> BlinkStickSquare:
        """Create a BlinkStickSquare instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=8)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 8)
        return BlinkStickSquare(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert BlinkStickSquare.vendor() == "Agile Innovative"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = BlinkStickSquare.supported_device_ids
        assert (0x20A0, 0x41E5) in device_ids
        assert device_ids[(0x20A0, 0x41E5)] == "BlinkStick Square"

    def test_claims_method_valid_hardware(self, mock_hardware) -> None:
        """Test claims() method with valid hardware."""
        mock_hardware.serial_number = "BS123456-3.0"
        mock_hardware.release_number = 0x200

        # Mock super().claims() to return True
        with patch.object(BlinkStickSquare.__bases__[0], "claims", return_value=True):
            assert BlinkStickSquare.claims(mock_hardware) is True

    def test_claims_method_invalid_serial_number(self, mock_hardware) -> None:
        """Test claims() method with invalid serial number."""
        mock_hardware.serial_number = "BS123456-2.0"  # Wrong major version
        mock_hardware.release_number = 0x200

        with patch.object(BlinkStickSquare.__bases__[0], "claims", return_value=True):
            assert BlinkStickSquare.claims(mock_hardware) is False

    def test_claims_method_invalid_release_number(self, mock_hardware) -> None:
        """Test claims() method with invalid release number."""
        mock_hardware.serial_number = "BS123456-3.0"
        mock_hardware.release_number = 0x100  # Wrong release number

        with patch.object(BlinkStickSquare.__bases__[0], "claims", return_value=True):
            assert BlinkStickSquare.claims(mock_hardware) is False

    def test_claims_method_index_error(self, mock_hardware) -> None:
        """Test claims() method with IndexError in serial number processing."""
        mock_hardware.serial_number = "12"  # Too short to access [-3:][0]
        mock_hardware.release_number = 0x200

        with patch.object(BlinkStickSquare.__bases__[0], "claims", return_value=True):
            assert BlinkStickSquare.claims(mock_hardware) is False

    def test_claims_method_type_error(self, mock_hardware) -> None:
        """Test claims() method with TypeError in serial number processing."""
        mock_hardware.serial_number = None  # None will cause TypeError
        mock_hardware.release_number = 0x200

        with patch.object(BlinkStickSquare.__bases__[0], "claims", return_value=True):
            assert BlinkStickSquare.claims(mock_hardware) is False

    def test_claims_method_super_false(self, mock_hardware) -> None:
        """Test claims() method when super().claims() returns False."""
        mock_hardware.serial_number = "BS123456-3.0"
        mock_hardware.release_number = 0x200

        with patch.object(BlinkStickSquare.__bases__[0], "claims", return_value=False):
            assert BlinkStickSquare.claims(mock_hardware) is False

    def test_state_property(self, blinkstick_square) -> None:
        """Test state property returns BlinkStick Square state."""
        state = blinkstick_square.state
        assert isinstance(state, State)
        assert state.report == 6
        assert state.nleds == 8
        # Should be cached
        assert blinkstick_square.state is state

    def test_bytes_method(self, blinkstick_square) -> None:
        """Test __bytes__ method returns state bytes."""
        state_bytes = bytes(blinkstick_square)
        expected_bytes = bytes(blinkstick_square.state)
        assert state_bytes == expected_bytes

    def test_on_method_all_leds(self, blinkstick_square) -> None:
        """Test on() method with LED=0 (all LEDs)."""
        color = (255, 128, 64)
        with patch.object(blinkstick_square, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick_square.on(color, led=0)

            assert blinkstick_square.color == color
            assert blinkstick_square.state.color == color
            mock_batch.assert_called_once()

    def test_on_method_specific_led(self, blinkstick_square) -> None:
        """Test on() method with specific LED."""
        color = (200, 100, 50)
        led = 3
        # Initialize colors array so set_led can work
        blinkstick_square.state.colors = [(0, 0, 0)] * 8

        with patch.object(blinkstick_square, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick_square.on(color, led=led)

            assert blinkstick_square.color == color
            # Should set specific LED (led-1 because method uses led-1)
            # get_led now returns RGB format (converted from internal GRB)
            assert blinkstick_square.state.get_led(led - 1) == color
            mock_batch.assert_called_once()

    def test_on_method_various_leds(self, blinkstick_square) -> None:
        """Test on() method with various LED indices."""
        color = (100, 200, 50)
        test_cases = [1, 2, 3, 4, 5, 6, 7, 8]

        for led in test_cases:
            # Initialize colors array so set_led can work
            blinkstick_square.state.colors = [(0, 0, 0)] * 8

            with patch.object(blinkstick_square, "batch_update") as mock_batch:
                mock_batch.return_value.__enter__ = Mock()
                mock_batch.return_value.__exit__ = Mock()

                blinkstick_square.on(color, led=led)

                assert blinkstick_square.color == color
                # Check that the correct LED index is set (led-1)
                # get_led now returns RGB format (converted from internal GRB)
                assert blinkstick_square.state.get_led(led - 1) == color
                mock_batch.assert_called_once()

    def test_on_method_batch_update_usage(self, blinkstick_square) -> None:
        """Test on() method uses batch_update correctly."""
        color = (150, 75, 25)
        with patch.object(blinkstick_square, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blinkstick_square.on(color)

            mock_batch.assert_called_once()
            mock_batch.return_value.__enter__.assert_called_once()
            mock_batch.return_value.__exit__.assert_called_once()

    def test_bytes_integration_with_state(self, blinkstick_square) -> None:
        """Test bytes() integration with state after on() calls."""
        color = (255, 128, 64)
        blinkstick_square.on(color, led=0)

        result = bytes(blinkstick_square)
        expected = bytes(blinkstick_square.state)
        assert result == expected

        # Should contain the color data
        assert len(result) >= 2  # At least report and channel

    def test_state_persistence_across_operations(self, blinkstick_square) -> None:
        """Test that state persists across multiple operations."""
        color1 = (255, 0, 0)
        color2 = (0, 255, 0)

        # Initialize colors array so set_led can work
        blinkstick_square.state.colors = [(0, 0, 0)] * 8

        # Set first color
        blinkstick_square.on(color1, led=1)
        led1_color = blinkstick_square.state.get_led(0)

        # Set second color on different LED
        blinkstick_square.on(color2, led=2)
        led2_color = blinkstick_square.state.get_led(1)

        # LEDs should have colors in RGB format (converted from internal GRB)
        assert led1_color == color1
        assert led2_color == color2

    def test_color_property_integration(self, blinkstick_square) -> None:
        """Test color property integration with BlinkStick Square."""
        color = (128, 64, 32)
        blinkstick_square.on(color, led=0)

        # Both device and state should have the same color
        assert blinkstick_square.color == color
        assert blinkstick_square.state.color == color

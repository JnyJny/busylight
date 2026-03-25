"""Tests for MuteMe MuteSync implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.muteme import MuteSync


class TestMuteMeMuteSync:
    """Test the MuteSync class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for testing."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x10C4
        hardware.product_id = 0xEA60
        hardware.device_id = (0x10C4, 0xEA60)
        hardware.connection_type = ConnectionType.HID
        hardware.manufacturer_string = "MuteSync Technologies"
        hardware.product_string = "MuteSync Button"
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def mutesync(self, mock_hardware) -> MuteSync:
        """Create a MuteSync instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=13)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 13)
        return MuteSync(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert MuteSync.vendor() == "MuteMe"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = MuteSync.supported_device_ids
        assert (0x10C4, 0xEA60) in device_ids
        assert device_ids[(0x10C4, 0xEA60)] == "MuteSync Button"

    def test_claims_method_with_mutesync_manufacturer(self, mock_hardware) -> None:
        """Test claims() method with MuteSync in manufacturer string."""
        mock_hardware.manufacturer_string = "MuteSync Technologies"
        mock_hardware.product_string = "Some Product"

        # Mock super().claims() to return True
        with patch.object(MuteSync.__bases__[1], "claims", return_value=True):
            assert MuteSync.claims(mock_hardware) is True

    def test_claims_method_with_mutesync_product(self, mock_hardware) -> None:
        """Test claims() method with MuteSync in product string."""
        mock_hardware.manufacturer_string = "Some Manufacturer"
        mock_hardware.product_string = "MuteSync Button"

        # Mock super().claims() to return True
        with patch.object(MuteSync.__bases__[1], "claims", return_value=True):
            assert MuteSync.claims(mock_hardware) is True

    def test_claims_method_without_mutesync_strings(self, mock_hardware) -> None:
        """Test claims() method without MuteSync in strings."""
        mock_hardware.manufacturer_string = "Other Manufacturer"
        mock_hardware.product_string = "Other Product"

        # Mock super().claims() to return True
        with patch.object(MuteSync.__bases__[1], "claims", return_value=True):
            assert MuteSync.claims(mock_hardware) is False

    def test_claims_method_with_super_false(self, mock_hardware) -> None:
        """Test claims() method when super().claims() returns False."""
        mock_hardware.manufacturer_string = "MuteSync Technologies"
        mock_hardware.product_string = "MuteSync Button"

        # Mock super().claims() to return False
        with patch.object(MuteSync.__bases__[1], "claims", return_value=False):
            assert MuteSync.claims(mock_hardware) is False

    def test_claims_method_with_attribute_error_manufacturer(
        self, mock_hardware
    ) -> None:
        """Test claims() method when manufacturer_string raises AttributeError."""
        del mock_hardware.manufacturer_string  # Remove the attribute
        mock_hardware.product_string = "MuteSync Button"

        # Mock super().claims() to return True
        with patch.object(MuteSync.__bases__[1], "claims", return_value=True):
            assert MuteSync.claims(mock_hardware) is True

    def test_claims_method_with_attribute_error_product(self, mock_hardware) -> None:
        """Test claims() method when product_string raises AttributeError."""
        mock_hardware.manufacturer_string = "MuteSync Technologies"
        del mock_hardware.product_string  # Remove the attribute

        # Mock super().claims() to return True
        with patch.object(MuteSync.__bases__[1], "claims", return_value=True):
            assert MuteSync.claims(mock_hardware) is True

    def test_claims_method_with_attribute_error_both(self, mock_hardware) -> None:
        """Test claims() method when both strings raise AttributeError."""
        del mock_hardware.manufacturer_string  # Remove the attribute
        del mock_hardware.product_string  # Remove the attribute

        # Mock super().claims() to return True
        with patch.object(MuteSync.__bases__[1], "claims", return_value=True):
            assert MuteSync.claims(mock_hardware) is False

    def test_bytes_method(self, mutesync) -> None:
        """Test __bytes__ method returns correct byte sequence."""
        # Set a test color
        test_color = (255, 128, 64)
        mutesync.color = test_color

        result = bytes(mutesync)

        # Should be [65] + [255, 128, 64] * 4 = [65, 255, 128, 64, 255, 128, 64, 255, 128, 64, 255, 128, 64]
        expected = bytes([65, 255, 128, 64, 255, 128, 64, 255, 128, 64, 255, 128, 64])
        assert result == expected
        assert len(result) == 13

    def test_bytes_method_with_different_colors(self, mutesync) -> None:
        """Test __bytes__ method with different color values."""
        test_cases = [
            (0, 0, 0),
            (255, 255, 255),
            (100, 200, 50),
        ]

        for color in test_cases:
            mutesync.color = color
            result = bytes(mutesync)

            # Should be [65] + color * 4
            expected = bytes([65] + list(color) * 4)
            assert result == expected

    def test_is_button_property(self, mutesync) -> None:
        """Test is_button property returns True."""
        assert mutesync.is_button is True

    def test_button_on_property(self, mutesync) -> None:
        """Test button_on property returns False."""
        assert mutesync.button_on is False

    def test_on_method(self, mutesync) -> None:
        """Test on() method sets color correctly."""
        test_color = (200, 100, 50)

        # Mock batch_update context manager
        with patch.object(mutesync, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            mutesync.on(test_color)

            # Should set color and use batch_update
            assert mutesync.color == test_color
            mock_batch.assert_called_once()
            mock_batch.return_value.__enter__.assert_called_once()
            mock_batch.return_value.__exit__.assert_called_once()

    def test_on_method_with_led_parameter(self, mutesync) -> None:
        """Test on() method with led parameter (ignored)."""
        test_color = (150, 75, 25)
        led = 5  # Should be ignored

        with patch.object(mutesync, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            mutesync.on(test_color, led=led)

            # Should still set color regardless of led parameter
            assert mutesync.color == test_color
            mock_batch.assert_called_once()

    def test_on_method_integration_with_bytes(self, mutesync) -> None:
        """Test integration between on() method and __bytes__."""
        test_color = (128, 192, 64)

        with patch.object(mutesync, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            mutesync.on(test_color)

            # Check that bytes() reflects the new color
            result = bytes(mutesync)
            expected = bytes([65] + list(test_color) * 4)
            assert result == expected

    def test_button_properties_independence(self, mutesync) -> None:
        """Test that button properties are independent of color state."""
        # Change color
        mutesync.color = (255, 0, 0)

        # Button properties should remain unchanged
        assert mutesync.is_button is True
        assert mutesync.button_on is False

    def test_claims_method_case_insensitive(self, mock_hardware) -> None:
        """Test claims() method is case insensitive."""
        test_cases = [
            ("MUTESYNC Technologies", "Other Product"),
            ("Other Manufacturer", "MUTESYNC Button"),
            ("mutesync technologies", "other product"),
            ("other manufacturer", "mutesync button"),
            ("MutEsYnC Technologies", "Other Product"),
        ]

        # Mock super().claims() to return True
        with patch.object(MuteSync.__bases__[1], "claims", return_value=True):
            for manufacturer, product in test_cases:
                mock_hardware.manufacturer_string = manufacturer
                mock_hardware.product_string = product

                result = MuteSync.claims(mock_hardware)
                assert result is True, (
                    f"Failed for manufacturer='{manufacturer}', product='{product}'"
                )

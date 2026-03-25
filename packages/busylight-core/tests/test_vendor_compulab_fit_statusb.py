"""Tests for CompuLab fit-statUSB implementation."""

from unittest.mock import Mock

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.mixins import ColorableMixin
from busylight_core.vendors.compulab import FitStatUSB
from busylight_core.vendors.compulab.compulab_base import CompuLabBase


class TestCompuLabFitStatUSB:
    """Test the CompuLab fit-statUSB device functionality."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for testing fit-statUSB device."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x2047
        hardware.product_id = 0x03DF
        hardware.device_id = (0x2047, 0x03DF)
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def fit_statusb(self, mock_hardware) -> FitStatUSB:
        """Create a FitStatUSB instance for testing."""
        # Mock the hardware handle methods
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=16)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 16)

        return FitStatUSB(mock_hardware, reset=False, exclusive=False)

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected fit-statUSB device."""
        device_ids = FitStatUSB.supported_device_ids
        assert (0x2047, 0x03DF) in device_ids
        assert device_ids[(0x2047, 0x03DF)] == "fit-statUSB"
        # Should only have one device ID
        assert len(device_ids) == 1

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert FitStatUSB.vendor() == "CompuLab"

    def test_claims_method_with_fit_statusb_hardware(self, mock_hardware) -> None:
        """Test claims() method with fit-statUSB hardware."""
        # Test with correct fit-statUSB device ID
        mock_hardware.device_id = (0x2047, 0x03DF)
        assert FitStatUSB.claims(mock_hardware) is True

        # Test with unknown device ID
        mock_hardware.device_id = (0x1234, 0x5678)
        assert FitStatUSB.claims(mock_hardware) is False

    def test_bytes_method_black_color(self, fit_statusb) -> None:
        """Test __bytes__ method with black color (all zeros)."""
        fit_statusb.color = (0, 0, 0)
        result = bytes(fit_statusb)
        expected = b"B#000000\n"
        assert result == expected

    def test_bytes_method_red_color(self, fit_statusb) -> None:
        """Test __bytes__ method with red color."""
        fit_statusb.color = (255, 0, 0)
        result = bytes(fit_statusb)
        expected = b"B#ff0000\n"
        assert result == expected

    def test_bytes_method_green_color(self, fit_statusb) -> None:
        """Test __bytes__ method with green color."""
        fit_statusb.color = (0, 255, 0)
        result = bytes(fit_statusb)
        expected = b"B#00ff00\n"
        assert result == expected

    def test_bytes_method_blue_color(self, fit_statusb) -> None:
        """Test __bytes__ method with blue color."""
        fit_statusb.color = (0, 0, 255)
        result = bytes(fit_statusb)
        expected = b"B#0000ff\n"
        assert result == expected

    def test_bytes_method_white_color(self, fit_statusb) -> None:
        """Test __bytes__ method with white color (all max)."""
        fit_statusb.color = (255, 255, 255)
        result = bytes(fit_statusb)
        expected = b"B#ffffff\n"
        assert result == expected

    def test_bytes_method_mixed_color(self, fit_statusb) -> None:
        """Test __bytes__ method with mixed RGB values."""
        fit_statusb.color = (128, 64, 192)
        result = bytes(fit_statusb)
        expected = b"B#8040c0\n"  # 128=0x80, 64=0x40, 192=0xC0
        assert result == expected

    def test_bytes_method_low_values(self, fit_statusb) -> None:
        """Test __bytes__ method with low RGB values (padding check)."""
        fit_statusb.color = (1, 2, 3)
        result = bytes(fit_statusb)
        expected = b"B#010203\n"
        assert result == expected

    def test_on_method_sets_color(self, fit_statusb) -> None:
        """Test on() method sets the device color."""
        color = (200, 150, 100)
        fit_statusb.on(color)
        assert fit_statusb.color == color

    def test_on_method_with_led_parameter_ignored(self, fit_statusb) -> None:
        """Test on() method ignores led parameter as documented."""
        color = (128, 128, 128)
        fit_statusb.on(color, led=5)  # LED parameter should be ignored
        assert fit_statusb.color == color

    def test_on_method_calls_batch_update(self, fit_statusb) -> None:
        """Test on() method uses batch_update context."""
        mock_batch = Mock()
        mock_batch.__enter__ = Mock()
        mock_batch.__exit__ = Mock()
        fit_statusb.batch_update = Mock(return_value=mock_batch)

        color = (255, 128, 64)
        fit_statusb.on(color)

        # Verify batch_update was called
        fit_statusb.batch_update.assert_called_once()

    def test_color_property_from_colorable_mixin(self, fit_statusb) -> None:
        """Test color property inherited from ColorableMixin."""
        # Test setting color
        test_color = (100, 200, 50)
        fit_statusb.color = test_color
        assert fit_statusb.color == test_color

        # Test individual RGB components
        assert fit_statusb.red == 100
        assert fit_statusb.green == 200
        assert fit_statusb.blue == 50

    def test_red_green_blue_properties(self, fit_statusb) -> None:
        """Test individual red, green, blue properties from ColorableMixin."""
        # Set individual colors
        fit_statusb.red = 128
        fit_statusb.green = 64
        fit_statusb.blue = 192

        # Check color tuple
        assert fit_statusb.color == (128, 64, 192)

        # Check bytes output format
        result = bytes(fit_statusb)
        expected = b"B#8040c0\n"  # 128=0x80, 64=0x40, 192=0xC0
        assert result == expected

    def test_is_lit_property(self, fit_statusb) -> None:
        """Test is_lit property from ColorableMixin."""
        # Black color should not be lit
        fit_statusb.color = (0, 0, 0)
        assert fit_statusb.is_lit is False

        # Any non-zero color should be lit
        fit_statusb.color = (1, 0, 0)
        assert fit_statusb.is_lit is True

        fit_statusb.color = (0, 1, 0)
        assert fit_statusb.is_lit is True

        fit_statusb.color = (0, 0, 1)
        assert fit_statusb.is_lit is True

        fit_statusb.color = (255, 255, 255)
        assert fit_statusb.is_lit is True

    def test_protocol_format_consistency(self, fit_statusb) -> None:
        """Test that the protocol format is consistent and follows specification."""
        # Test various colors to ensure protocol format is always correct
        test_cases = [
            ((0, 0, 0), b"B#000000\n"),
            ((255, 255, 255), b"B#ffffff\n"),
            ((17, 34, 51), b"B#112233\n"),  # 0x11, 0x22, 0x33
            ((171, 205, 239), b"B#abcdef\n"),  # 0xAB, 0xCD, 0xEF
            ((16, 32, 48), b"B#102030\n"),
        ]

        for color, expected_bytes in test_cases:
            fit_statusb.color = color
            result = bytes(fit_statusb)
            assert result == expected_bytes, f"Failed for color {color}"

    def test_text_based_protocol_encoding(self, fit_statusb) -> None:
        """Test that the device uses text-based protocol with proper encoding."""
        fit_statusb.color = (0xAB, 0xCD, 0xEF)
        result = bytes(fit_statusb)

        # Should be text-based protocol
        assert result.startswith(b"B#")
        assert result.endswith(b"\n")

        # Should be lowercase hex
        assert b"abcdef" in result

        # Should be properly encoded bytes
        assert isinstance(result, bytes)

        # Should decode to valid text
        text = result.decode("ascii")
        assert text == "B#abcdef\n"

    def test_hex_formatting_edge_cases(self, fit_statusb) -> None:
        """Test hexadecimal formatting edge cases."""
        # Test single digits (should be zero-padded)
        fit_statusb.color = (5, 10, 15)
        result = bytes(fit_statusb)
        expected = b"B#050a0f\n"
        assert result == expected

        # Test high values
        fit_statusb.color = (240, 250, 255)
        result = bytes(fit_statusb)
        expected = b"B#f0faff\n"
        assert result == expected

    def test_inheritance_from_colorable_mixin_and_light(self, fit_statusb) -> None:
        """Test that FitStatUSB properly inherits from both ColorableMixin and Light."""
        # Test ColorableMixin inheritance
        assert hasattr(fit_statusb, "red")
        assert hasattr(fit_statusb, "green")
        assert hasattr(fit_statusb, "blue")
        assert hasattr(fit_statusb, "color")
        assert hasattr(fit_statusb, "is_lit")

        # Test Light inheritance
        assert hasattr(fit_statusb, "on")
        assert hasattr(fit_statusb, "off")
        assert hasattr(fit_statusb, "reset")
        assert hasattr(fit_statusb, "vendor")
        assert hasattr(fit_statusb, "claims")
        assert hasattr(fit_statusb, "supported_device_ids")

    def test_device_specific_functionality(self, fit_statusb) -> None:
        """Test device-specific functionality of fit-statUSB."""
        # Test that it uses the correct protocol format (B# prefix)
        fit_statusb.color = (100, 150, 200)
        result = bytes(fit_statusb)

        # Specific to fit-statUSB protocol
        assert result.startswith(b"B#")
        assert result.endswith(b"\n")
        assert len(result) == 9  # "B#" + 6 hex chars + "\n"

        # Test protocol is case-insensitive but outputs lowercase
        expected = b"B#6496c8\n"  # 100=0x64, 150=0x96, 200=0xC8 -> lowercase
        assert result == expected

    def test_vendor_hierarchy(self, fit_statusb) -> None:
        """Test FitStatUSB inherits from CompuLabBase properly."""
        # Test inheritance hierarchy
        assert isinstance(fit_statusb, FitStatUSB)
        assert isinstance(fit_statusb, CompuLabBase)

        # Test class hierarchy
        assert issubclass(FitStatUSB, CompuLabBase)

        # Test vendor method comes from CompuLabBase
        assert FitStatUSB.vendor() == "CompuLab"
        assert CompuLabBase.vendor() == "CompuLab"

    def test_method_resolution_order(self) -> None:
        """Test MRO follows expected pattern."""
        mro = FitStatUSB.__mro__

        # Should be: FitStatUSB -> ColorableMixin -> CompuLabBase -> Light -> ...
        assert mro[0] == FitStatUSB
        assert mro[1] == ColorableMixin
        assert mro[2].__name__ == "CompuLabBase"
        assert mro[3].__name__ == "Light"

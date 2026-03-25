"""Tests for MuteMe implementation."""

import struct
from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.muteme import MuteMe
from busylight_core.vendors.muteme.implementation import (
    BlinkBit,
    BlueBit,
    DimBit,
    GreenBit,
    OneBitField,
    RedBit,
    SleepBit,
    State,
)


class TestMuteMeOneBitField:
    """Test the OneBitField custom bit field."""

    def test_onebitfield_get_true(self) -> None:
        """Test OneBitField __get__ method returns 0xFF for true."""
        field = OneBitField(0, 1)
        mock_instance = Mock()

        # Mock the parent's __get__ to return 1 (true)
        with patch.object(OneBitField.__bases__[0], "__get__", return_value=1):
            result = field.__get__(mock_instance, None)
            assert result == 0xFF

    def test_onebitfield_get_false(self) -> None:
        """Test OneBitField __get__ method returns 0 for false."""
        field = OneBitField(0, 1)
        mock_instance = Mock()

        # Mock the parent's __get__ to return 0 (false)
        with patch.object(OneBitField.__bases__[0], "__get__", return_value=0):
            result = field.__get__(mock_instance, None)
            assert result == 0

    def test_onebitfield_set_true(self) -> None:
        """Test OneBitField __set__ method with true value."""
        field = OneBitField(0, 1)
        mock_instance = Mock()

        with patch.object(OneBitField.__bases__[0], "__set__") as mock_set:
            field.__set__(mock_instance, 255)  # Any non-zero value
            mock_set.assert_called_once_with(mock_instance, 1)

    def test_onebitfield_set_false(self) -> None:
        """Test OneBitField __set__ method with false value."""
        field = OneBitField(0, 1)
        mock_instance = Mock()

        with patch.object(OneBitField.__bases__[0], "__set__") as mock_set:
            field.__set__(mock_instance, 0)
            mock_set.assert_called_once_with(mock_instance, 0)

    def test_onebitfield_setg(self) -> None:
        """Test OneBitField __set__ method."""
        field = OneBitField(0, 1)
        mock_instance = Mock()

        with patch.object(OneBitField.__bases__[0], "__set__") as mock_set:
            # Test various values that should be masked
            test_values = [
                (0x00, 0),
                (0x01, 1),
                (0x02, 1),
                (0x03, 1),
                (0xFF, 1),
                (0xFE, 1),
            ]

            for input_val, expected_val in test_values:
                field.__set__(mock_instance, input_val)
                mock_set.assert_called_with(mock_instance, expected_val)


class TestMuteMeColorBitFields:
    """Test the color bit field classes."""

    def test_redbit_position(self) -> None:
        """Test RedBit is at position 0."""
        field = RedBit()
        assert field.field == slice(0, 1)

    def test_greenbit_position(self) -> None:
        """Test GreenBit is at position 1."""
        field = GreenBit()
        assert field.field == slice(1, 2)

    def test_bluebit_position(self) -> None:
        """Test BlueBit is at position 2."""
        field = BlueBit()
        assert field.field == slice(2, 3)

    def test_dimbit_position(self) -> None:
        """Test DimBit is at position 4."""
        field = DimBit()
        assert field.field == slice(4, 5)

    def test_blinkbit_position(self) -> None:
        """Test BlinkBit is at position 5."""
        field = BlinkBit()
        assert field.field == slice(5, 6)

    def test_sleepbit_position(self) -> None:
        """Test SleepBit is at position 6."""
        field = SleepBit()
        assert field.field == slice(6, 7)


class TestMuteMeState:
    """Test the State class."""

    def test_state_initialization(self) -> None:
        """Test State initializes with default values."""
        state = State()
        assert state.red == 0
        assert state.green == 0
        assert state.blue == 0
        assert state.dim == 0
        assert state.blink == 0
        assert state.sleep == 0
        assert state.color == (0, 0, 0)

    def test_state_color_property_getter(self) -> None:
        """Test color property getter."""
        state = State()
        state.red = 0xFF
        state.green = 0xFF
        state.blue = 0xFF
        assert state.color == (0xFF, 0xFF, 0xFF)

    def test_state_color_property_setter(self) -> None:
        """Test color property setter."""
        state = State()
        state.color = (0xFF, 0xFF, 0xFF)
        assert state.red == 0xFF
        assert state.green == 0xFF
        assert state.blue == 0xFF

    def test_state_color_property_mixed(self) -> None:
        """Test color property with mixed values."""
        state = State()
        state.color = (0xFF, 0, 0xFF)
        assert state.red == 0xFF
        assert state.green == 0
        assert state.blue == 0xFF
        assert state.color == (0xFF, 0, 0xFF)

    def test_state_individual_bit_fields(self) -> None:
        """Test individual bit field operations."""
        state = State()

        # Test setting individual bits
        state.red = 1
        state.green = 1
        state.blue = 1
        state.dim = 1
        state.blink = 1
        state.sleep = 1

        # All should return 0xFF when set
        assert state.red == 0xFF
        assert state.green == 0xFF
        assert state.blue == 0xFF
        assert state.dim == 0xFF
        assert state.blink == 0xFF
        assert state.sleep == 0xFF

    def test_state_bit_field_masking(self) -> None:
        """Test bit field masking behavior."""
        state = State()

        # Test that non-zero values are treated as true
        state.red = 255
        state.green = 128
        state.blue = 1

        assert state.red == 0xFF
        assert state.green == 0xFF
        assert state.blue == 0xFF

        # Test that zero values are treated as false
        state.red = 0
        state.green = 0
        state.blue = 0

        assert state.red == 0
        assert state.green == 0
        assert state.blue == 0

    def test_state_bit_positions(self) -> None:
        """Test that bit fields are at correct positions."""
        state = State()

        # Set individual bits and check the underlying value
        state.red = 1
        assert state.value & 0x01 == 0x01  # Bit 0

        state.green = 1
        assert state.value & 0x02 == 0x02  # Bit 1

        state.blue = 1
        assert state.value & 0x04 == 0x04  # Bit 2

        state.dim = 1
        assert state.value & 0x10 == 0x10  # Bit 4

        state.blink = 1
        assert state.value & 0x20 == 0x20  # Bit 5

        state.sleep = 1
        assert state.value & 0x40 == 0x40  # Bit 6


class TestMuteMe:
    """Test the main MuteMe class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for testing."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x16C0
        hardware.product_id = 0x27DB
        hardware.device_id = (0x16C0, 0x27DB)
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        hardware.send_feature_report = Mock()
        return hardware

    @pytest.fixture
    def muteme(self, mock_hardware: Hardware) -> MuteMe:
        """Create a MuteMe instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=2)
        mock_hardware.handle.read = Mock(return_value=b"\x00\x00")
        return MuteMe(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert MuteMe.vendor() == "MuteMe"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = MuteMe.supported_device_ids
        assert (0x16C0, 0x27DB) in device_ids
        assert (0x20A0, 0x42DA) in device_ids
        assert device_ids[(0x16C0, 0x27DB)] == "MuteMe Original"
        assert device_ids[(0x20A0, 0x42DA)] == "MuteMe Original"

    def test_state_property(self, muteme) -> None:
        """Test state property returns State instance."""
        assert isinstance(muteme.state, State)
        # Should be cached
        assert muteme.state is muteme.state

    def test_struct_property(self, muteme) -> None:
        """Test struct property returns struct.Struct instance."""
        assert isinstance(muteme.struct, struct.Struct)
        # Should be cached
        assert muteme.struct is muteme.struct
        # Should have correct format
        assert muteme.struct.format == "!xB"

    def test_bytes_method(self, muteme) -> None:
        """Test __bytes__ method returns formatted state."""
        muteme.color = (0xFF, 0, 0xFF)  # Red and blue
        result = bytes(muteme)

        # Expected: red=1, green=0, blue=1 = 0b101 = 5
        expected = muteme.struct.pack(5)
        assert result == expected
        assert len(result) == 2  # !xB format: 1 byte padding + 1 byte data

    def test_bytes_method_various_colors(self, muteme) -> None:
        """Test __bytes__ method with various colors."""
        test_cases = [
            ((0, 0, 0), 0b000),  # No colors
            ((255, 0, 0), 0b001),  # Red only
            ((0, 255, 0), 0b010),  # Green only
            ((0, 0, 255), 0b100),  # Blue only
            ((255, 255, 0), 0b011),  # Red + Green
            ((255, 0, 255), 0b101),  # Red + Blue
            ((0, 255, 255), 0b110),  # Green + Blue
            ((255, 255, 255), 0b111),  # All colors
        ]

        for color, expected_value in test_cases:
            muteme.color = color
            result = bytes(muteme)
            expected = muteme.struct.pack(expected_value)
            assert result == expected

    def test_is_pluggedin_property_success(self, muteme) -> None:
        """Test is_pluggedin property returns True when device responds."""
        muteme.hardware.send_feature_report.return_value = 8
        assert muteme.is_pluggedin is True
        muteme.hardware.send_feature_report.assert_called_once_with([0] * 8)

    def test_is_pluggedin_property_failure(self, muteme) -> None:
        """Test is_pluggedin property returns False when device doesn't respond."""
        muteme.hardware.send_feature_report.return_value = 4  # Wrong size
        assert muteme.is_pluggedin is False
        muteme.hardware.send_feature_report.assert_called_once_with([0] * 8)

    def test_is_pluggedin_property_exception(self, muteme) -> None:
        """Test is_pluggedin property returns False when exception occurs."""
        muteme.hardware.send_feature_report.side_effect = ValueError("Test error")
        assert muteme.is_pluggedin is False
        muteme.hardware.send_feature_report.assert_called_once_with([0] * 8)

    def test_is_button_property(self, muteme) -> None:
        """Test is_button property returns True."""
        assert muteme.is_button is True

    def test_button_on_property_not_implemented(self, muteme) -> None:
        """Test button_on property raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            _ = muteme.button_on

    def test_on_method(self, muteme) -> None:
        """Test on() method updates color."""
        color = (255, 255, 255)
        with patch.object(muteme, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            muteme.on(color)

            assert muteme.color == color
            mock_batch.assert_called_once()

    def test_on_method_with_led_parameter(self, muteme) -> None:
        """Test on() method with led parameter (should be ignored)."""
        color = (255, 255, 255)
        with patch.object(muteme, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            muteme.on(color, led=5)  # LED parameter should be ignored

            assert muteme.color == color
            mock_batch.assert_called_once()

    def test_on_method_batch_update_usage(self, muteme) -> None:
        """Test on() method uses batch_update correctly."""
        color = (100, 100, 100)
        with patch.object(muteme, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            muteme.on(color)

            mock_batch.assert_called_once()
            mock_batch.return_value.__enter__.assert_called_once()
            mock_batch.return_value.__exit__.assert_called_once()

    def test_bytes_method_updates_state(self, muteme) -> None:
        """Test __bytes__ method updates state with current color."""
        muteme.color = (255, 0, 255)

        # Call bytes() which should update state
        bytes(muteme)

        # State should be updated with current color
        # OneBitField converts non-zero to 0xFF, zero stays 0
        assert muteme.state.color == (
            255,
            0,
            255,
        )  # Colors converted through OneBitField
        assert muteme.state.red == 0xFF
        assert muteme.state.green == 0
        assert muteme.state.blue == 0xFF

    def test_struct_format_consistency(self, muteme) -> None:
        """Test struct format is consistent."""
        struct_obj = muteme.struct
        assert struct_obj.format == "!xB"
        assert struct_obj.size == 2  # 1 byte padding + 1 byte data

    def test_feature_report_call_parameters(self, muteme) -> None:
        """Test feature report is called with correct parameters."""
        muteme.hardware.send_feature_report.return_value = 8

        _ = muteme.is_pluggedin

        # Should be called with list of 8 zeros
        expected_call = [0] * 8
        muteme.hardware.send_feature_report.assert_called_once_with(expected_call)

    def test_state_persistence_across_calls(self, muteme) -> None:
        """Test that state persists across multiple calls."""
        # Set initial color
        muteme.color = (255, 0, 0)

        # Get bytes multiple times
        result1 = bytes(muteme)
        result2 = bytes(muteme)

        # Results should be consistent
        assert result1 == result2

        # State should be the same
        assert muteme.state.color == (255, 0, 0)

    def test_alternative_device_id(self) -> None:
        """Test with alternative device ID."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x20A0
        hardware.product_id = 0x42DA
        hardware.device_id = (0x20A0, 0x42DA)
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        hardware.send_feature_report = Mock()
        hardware.handle = Mock()
        hardware.handle.write = Mock(return_value=2)
        hardware.handle.read = Mock(return_value=b"\x00\x00")

        muteme = MuteMe(hardware, reset=False, exclusive=False)

        # Should work with alternative device ID
        assert muteme.vendor() == "MuteMe"
        assert isinstance(muteme.state, State)
        assert isinstance(muteme.struct, struct.Struct)

    def test_integration_color_to_bytes(self, muteme) -> None:
        """Test integration from color setting to bytes output."""
        # Test full integration
        color = (255, 1, 0)  # Red (255) and green (1, which is odd)
        muteme.color = color

        # Get bytes
        result = bytes(muteme)

        # Should have red and green bits set (0b011 = 3)
        expected = muteme.struct.pack(3)
        assert result == expected

        # State should be updated
        assert muteme.state.red == 0xFF
        assert muteme.state.green == 0xFF  # 1 & 1 = 1, so becomes 0xFF
        assert muteme.state.blue == 0

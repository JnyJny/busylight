"""Tests for Luxafor BusyTag implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.luxafor import BusyTag
from busylight_core.vendors.luxafor._busytag import Command


class TestLuxaforBusyTagCommand:
    """Test the Command enum for BusyTag."""

    def test_command_enum_values(self) -> None:
        """Test that Command enum has all expected AT commands."""
        assert Command.GetDeviceName == "AT+GDN"
        assert Command.GetManufacturerName == "AT+GMN"
        assert Command.GetDeviceID == "AT+GID"
        assert Command.GetPictureList == "AT+GPL"
        assert Command.GetFileList == "AT+GFL"
        assert Command.GetLocalHostAddress == "AT+GLHA"
        assert Command.GetFreeStorageSize == "AT+GFSS"
        assert Command.GetTotalStorageSize == "AT+GTSS"
        assert Command.GetLastErrorCode == "AT+GLEC"
        assert Command.GetLastResetReasonCore0 == "AT+GLRR0"
        assert Command.GetLastResetReasonCore1 == "AT+GLRR1"
        assert Command.SolidColor == "AT+SC={leds},{red:02x}{green:02x}{blue:02x}"

    def test_solid_color_method_all_leds(self) -> None:
        """Test solid_color method with all LEDs (led=0)."""
        color = (255, 128, 64)
        result = Command.solid_color(color, led=0)
        expected = "AT+SC=127,ff8040"
        assert result == expected

    def test_solid_color_method_specific_led(self) -> None:
        """Test solid_color method with specific LED."""
        color = (200, 100, 50)
        result = Command.solid_color(color, led=3)
        expected = "AT+SC=8,c86432"  # 1 << 3 = 8
        assert result == expected

    def test_solid_color_method_led_bit_shifting(self) -> None:
        """Test solid_color method LED bit shifting."""
        color = (255, 255, 255)

        # Test various LED positions
        test_cases = [
            (1, 2),  # 1 << 1 = 2
            (2, 4),  # 1 << 2 = 4
            (3, 8),  # 1 << 3 = 8
            (4, 16),  # 1 << 4 = 16
            (5, 32),  # 1 << 5 = 32
            (6, 64),  # 1 << 6 = 64
            (7, 128),  # 1 << 7 = 128
        ]

        for led_num, expected_leds in test_cases:
            result = Command.solid_color(color, led=led_num)
            expected = f"AT+SC={expected_leds},ffffff"
            assert result == expected

    def test_solid_color_method_color_formatting(self) -> None:
        """Test solid_color method color formatting."""
        # Test various colors to ensure proper hex formatting
        test_cases = [
            ((255, 255, 255), "ffffff"),
            ((0, 0, 0), "000000"),
            ((255, 0, 0), "ff0000"),
            ((0, 255, 0), "00ff00"),
            ((0, 0, 255), "0000ff"),
            ((128, 64, 32), "804020"),
            ((15, 15, 15), "0f0f0f"),  # Single digit hex values
        ]

        for color, expected_hex in test_cases:
            result = Command.solid_color(color, led=0)
            expected = f"AT+SC=127,{expected_hex}"
            assert result == expected

    def test_solid_color_method_edge_cases(self) -> None:
        """Test solid_color method edge cases."""
        # Test with LED 0 (should use 127)
        result = Command.solid_color((100, 100, 100), led=0)
        assert result == "AT+SC=127,646464"

        # Test with maximum LED number
        result = Command.solid_color((50, 50, 50), led=7)
        assert result == "AT+SC=128,323232"  # 1 << 7 = 128

    def test_solid_color_method_return_type(self) -> None:
        """Test that solid_color method returns a string."""
        result = Command.solid_color((255, 128, 64), led=0)
        assert isinstance(result, str)
        assert result.startswith("AT+SC=")


class TestLuxaforBusyTag:
    """Test the main BusyTag class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for testing."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x303A
        hardware.product_id = 0x81DF
        hardware.device_id = (0x303A, 0x81DF)
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def busytag(self, mock_hardware) -> BusyTag:
        """Create a BusyTag instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=32)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 32)
        return BusyTag(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert BusyTag.vendor() == "Luxafor"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = BusyTag.supported_device_ids
        assert (0x303A, 0x81DF) in device_ids
        assert device_ids[(0x303A, 0x81DF)] == "Busy Tag"

    def test_command_property_default(self, busytag) -> None:
        """Test command property default value."""
        assert busytag.command == ""

    def test_command_property_setter(self, busytag) -> None:
        """Test command property setter."""
        test_command = "AT+SC=127,ff0000"
        busytag.command = test_command
        assert busytag.command == test_command

    def test_command_property_getter(self, busytag) -> None:
        """Test command property getter."""
        # Test with no command set
        assert busytag.command == ""

        # Test with command set
        busytag._command = Command.GetDeviceName  # noqa: SLF001
        assert busytag.command == Command.GetDeviceName

    def test_bytes_method_empty_command(self, busytag) -> None:
        """Test __bytes__ method with empty command."""
        result = bytes(busytag)
        assert result == b""

    def test_bytes_method_with_command(self, busytag) -> None:
        """Test __bytes__ method with command."""
        busytag.command = "AT+SC=127,ff8040"
        result = bytes(busytag)
        expected = b"AT+SC=127,ff8040"
        assert result == expected

    def test_bytes_method_various_commands(self, busytag) -> None:
        """Test __bytes__ method with various commands."""
        test_commands = [
            "AT+GDN",
            "AT+GMN",
            "AT+SC=127,ffffff",
            "AT+SC=8,000000",
            "AT+GLEC",
        ]

        for command in test_commands:
            busytag.command = command
            result = bytes(busytag)
            expected = command.encode()
            assert result == expected

    def test_on_method_all_leds(self, busytag) -> None:
        """Test on() method with all LEDs."""
        color = (255, 128, 64)
        with patch.object(busytag, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            busytag.on(color)

            assert busytag.color == color
            assert busytag.command == "AT+SC=127,ff8040"
            mock_batch.assert_called_once()

    def test_on_method_specific_led(self, busytag) -> None:
        """Test on() method with specific LED."""
        color = (200, 100, 50)
        led = 3
        with patch.object(busytag, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            busytag.on(color, led=led)

            assert busytag.color == color
            assert busytag.command == "AT+SC=8,c86432"
            mock_batch.assert_called_once()

    def test_on_method_various_colors(self, busytag) -> None:
        """Test on() method with various colors."""
        test_cases = [
            ((255, 0, 0), "AT+SC=127,ff0000"),
            ((0, 255, 0), "AT+SC=127,00ff00"),
            ((0, 0, 255), "AT+SC=127,0000ff"),
            ((128, 64, 32), "AT+SC=127,804020"),
            ((0, 0, 0), "AT+SC=127,000000"),
        ]

        for color, expected_command in test_cases:
            with patch.object(busytag, "batch_update") as mock_batch:
                mock_batch.return_value.__enter__ = Mock()
                mock_batch.return_value.__exit__ = Mock()

                busytag.on(color)

                assert busytag.color == color
                assert busytag.command == expected_command

    def test_on_method_various_leds(self, busytag) -> None:
        """Test on() method with various LED positions."""
        color = (255, 255, 255)
        test_cases = [
            (0, "AT+SC=127,ffffff"),  # All LEDs
            (1, "AT+SC=2,ffffff"),  # LED 1
            (2, "AT+SC=4,ffffff"),  # LED 2
            (3, "AT+SC=8,ffffff"),  # LED 3
            (4, "AT+SC=16,ffffff"),  # LED 4
            (5, "AT+SC=32,ffffff"),  # LED 5
            (6, "AT+SC=64,ffffff"),  # LED 6
            (7, "AT+SC=128,ffffff"),  # LED 7
        ]

        for led, expected_command in test_cases:
            with patch.object(busytag, "batch_update") as mock_batch:
                mock_batch.return_value.__enter__ = Mock()
                mock_batch.return_value.__exit__ = Mock()

                busytag.on(color, led=led)

                assert busytag.color == color
                assert busytag.command == expected_command

    def test_on_method_batch_update_usage(self, busytag) -> None:
        """Test on() method uses batch_update correctly."""
        color = (100, 100, 100)
        with patch.object(busytag, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            busytag.on(color)

            mock_batch.assert_called_once()
            mock_batch.return_value.__enter__.assert_called_once()
            mock_batch.return_value.__exit__.assert_called_once()

    def test_command_persistence(self, busytag) -> None:
        """Test that command persists across operations."""
        busytag.command = "AT+GDN"
        assert busytag.command == "AT+GDN"

        # Command should persist even after other operations
        _ = bytes(busytag)
        assert busytag.command == "AT+GDN"

        # Setting new command should update it
        busytag.command = "AT+SC=127,ffffff"
        assert busytag.command == "AT+SC=127,ffffff"

    def test_on_method_updates_both_color_and_command(self, busytag) -> None:
        """Test that on() method updates both color and command."""
        color = (150, 75, 25)
        with patch.object(busytag, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            busytag.on(color, led=2)

            # Both color and command should be updated
            assert busytag.color == color
            assert busytag.command == "AT+SC=4,964b19"

            # bytes() should return the encoded command
            assert bytes(busytag) == b"AT+SC=4,964b19"

    def test_encoding_consistency(self, busytag) -> None:
        """Test that command encoding is consistent."""
        commands = [
            "AT+GDN",
            "AT+SC=127,ff0000",
            "AT+GLEC",
            "AT+SC=8,00ff00",
        ]

        for command in commands:
            busytag.command = command
            encoded = bytes(busytag)
            expected = command.encode()
            assert encoded == expected

            # Decode back to verify consistency
            decoded = encoded.decode()
            assert decoded == command

    def test_command_integration_with_on_method(self, busytag) -> None:
        """Test integration between command property and on() method."""
        # Start with empty command
        assert busytag.command == ""

        # Call on() method
        color = (255, 128, 0)
        with patch.object(busytag, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            busytag.on(color, led=1)

            # Command should be set by on() method
            assert busytag.command == "AT+SC=2,ff8000"

            # bytes() should return the command
            assert bytes(busytag) == b"AT+SC=2,ff8000"

            # Color should also be set
            assert busytag.color == color

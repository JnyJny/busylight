"""Tests for the Embrava Blynclight device."""

from unittest.mock import Mock, patch

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.embrava.blynclight import Blynclight
from busylight_core.vendors.embrava.implementation import (
    BlynclightFlashSpeed as FlashSpeed,
)
from busylight_core.vendors.embrava.implementation import (
    BlynclightState as State,
)


def create_mock_blynclight_hardware() -> Mock:
    """Create a properly configured mock hardware for Blynclight device."""
    mock_hardware = Mock(spec=Hardware)
    mock_hardware.device_id = (0x2C0D, 0x0001)
    mock_hardware.device_type = ConnectionType.HID
    mock_hardware.path = b"/dev/hidraw0"
    mock_hardware.product_string = "Blynclight"
    mock_hardware.vendor_id = 0x2C0D
    mock_hardware.product_id = 0x0001
    return mock_hardware


class TestBlynclightDeviceSupport:
    """Test device identification and support."""

    def test_supported_device_ids(self) -> None:
        """Test that supported_device_ids contains correct device mapping."""
        assert isinstance(Blynclight.supported_device_ids, dict)
        assert (0x2C0D, 0x0001) in Blynclight.supported_device_ids
        assert (0x2C0D, 0x000C) in Blynclight.supported_device_ids
        assert (0x0E53, 0x2516) in Blynclight.supported_device_ids
        assert Blynclight.supported_device_ids[(0x2C0D, 0x0001)] == "Blynclight"

    def test_device_claiming_logic(self) -> None:
        """Test that Blynclight can properly claim devices using inherited logic."""
        mock_hardware = create_mock_blynclight_hardware()

        result = Blynclight.claims(mock_hardware)
        assert result is True

    def test_device_claiming_wrong_device(self) -> None:
        """Test that Blynclight rejects devices it doesn't support."""
        mock_hardware = Mock(spec=Hardware)
        mock_hardware.vendor_id = 0x1234
        mock_hardware.product_id = 0x5678
        mock_hardware.device_id = (0x1234, 0x5678)
        mock_hardware.product_string = "Other Device"

        result = Blynclight.claims(mock_hardware)
        assert result is False


class TestBlynclightProperties:
    """Test Blynclight properties and initialization."""

    def test_state_property_cached(self) -> None:
        """Test that state property is cached and returns State object."""
        mock_hardware = create_mock_blynclight_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blynclight, "reset"):
            blynclight = Blynclight(mock_hardware)

            state1 = blynclight.state
            state2 = blynclight.state

            assert isinstance(state1, State)
            assert state1 is state2  # Should be cached


class TestBlynclightBytes:
    """Test Blynclight bytes conversion and state management."""

    def test_bytes_conversion_light_on(self) -> None:
        """Test __bytes__ method when light is on."""
        mock_hardware = create_mock_blynclight_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blynclight, "reset"):
            blynclight = Blynclight(mock_hardware)
            blynclight.color = (255, 128, 64)  # Set RGB values - this makes is_lit True

            result = bytes(blynclight)

            assert isinstance(result, bytes)
            assert len(result) == 9  # Expected struct size
            assert blynclight.state.off == 0  # Should set off=False when lit

    def test_on_sets_off_bit_when_color_is_black(self) -> None:
        """Test on() sets off=True when color is black (not lit)."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update"),
        ):
            blynclight = Blynclight(mock_hardware)
            blynclight.on((0, 0, 0))  # Black color - not lit

            assert blynclight.state.off == 1

    def test_on_clears_flash_when_off(self) -> None:
        """Test that on() clears flash when light is off."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update"),
        ):
            blynclight = Blynclight(mock_hardware)
            blynclight.state.flash = True
            blynclight.on((0, 0, 0))  # Black color - not lit

            assert blynclight.state.flash == 0

    def test_on_clears_dim_when_off(self) -> None:
        """Test that on() clears dim when light is off."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update"),
        ):
            blynclight = Blynclight(mock_hardware)
            blynclight.state.dim = True
            blynclight.on((0, 0, 0))  # Black color - not lit

            assert blynclight.state.dim == 0

    def test_bytes_flash_preserved_when_on(self) -> None:
        """Test that flash is preserved when light is on."""
        mock_hardware = create_mock_blynclight_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blynclight, "reset"):
            blynclight = Blynclight(mock_hardware)
            blynclight.state.flash = True
            blynclight.color = (255, 0, 0)  # Set to non-zero - this makes is_lit True

            bytes(blynclight)

            # Flash should be preserved when light is on
            assert blynclight.state.flash == 1


class TestBlynclightDimming:
    """Test dimming functionality."""

    def test_dim_method(self) -> None:
        """Test dim method sets dim state."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update") as mock_update,
        ):
            blynclight = Blynclight(mock_hardware)

            blynclight.dim()

            mock_update.assert_called_once()
            assert blynclight.state.dim == 1

    def test_bright_method(self) -> None:
        """Test bright method clears dim state."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update") as mock_update,
        ):
            blynclight = Blynclight(mock_hardware)
            blynclight.state.dim = True  # Start dimmed

            blynclight.bright()

            mock_update.assert_called_once()
            assert blynclight.state.dim == 0


class TestBlynclightFlashing:
    """Test flashing functionality."""

    def test_flash_method_default_speed(self) -> None:
        """Test flash method with default speed."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update") as mock_update,
        ):
            blynclight = Blynclight(mock_hardware)

            blynclight.flash((255, 0, 0))  # Red color

            mock_update.assert_called_once()
            assert blynclight.color == (255, 0, 0)
            assert blynclight.state.flash == 1
            assert blynclight.state.speed == FlashSpeed.slow.value

    def test_flash_method_custom_speed(self) -> None:
        """Test flash method with custom speed."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update") as mock_update,
        ):
            blynclight = Blynclight(mock_hardware)

            blynclight.flash((0, 255, 0), FlashSpeed.fast)  # Green color, fast speed

            mock_update.assert_called_once()
            assert blynclight.color == (0, 255, 0)
            assert blynclight.state.flash == 1
            assert blynclight.state.speed == FlashSpeed.fast.value

    def test_stop_flashing_method(self) -> None:
        """Test stop_flashing method."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update") as mock_update,
        ):
            blynclight = Blynclight(mock_hardware)
            blynclight.state.flash = True  # Start flashing

            blynclight.stop_flashing()

            mock_update.assert_called_once()
            assert blynclight.state.flash == 0


class TestBlynclightReset:
    """Test reset functionality."""

    def test_reset_method(self) -> None:
        """Test reset method clears all state."""
        mock_hardware = create_mock_blynclight_hardware()

        with patch.object(mock_hardware, "acquire"):
            # Don't mock reset during initialization
            with patch.object(Blynclight, "reset"):
                blynclight = Blynclight(mock_hardware)

            # Set various states
            blynclight.state.off = False
            blynclight.state.dim = True
            blynclight.state.flash = True
            blynclight.state.speed = FlashSpeed.fast.value
            blynclight.state.play = True
            blynclight.state.mute = True
            blynclight.state.repeat = True
            blynclight.state.music = 10
            blynclight.state.volume = 15

            # Mock update method and super().reset() for the actual reset call
            with (
                patch.object(blynclight, "update") as mock_update,
            ):
                blynclight.reset()

            mock_update.assert_called_once()

            # Verify all state is reset
            assert blynclight.state.off == 1
            assert blynclight.state.dim == 0
            assert blynclight.state.flash == 0
            assert blynclight.state.speed == FlashSpeed.slow.value
            assert blynclight.state.play == 0
            assert blynclight.state.mute == 0
            assert blynclight.state.repeat == 0
            assert blynclight.state.music == 0
            assert blynclight.state.volume == 0


class TestFlashSpeedEnum:
    """Test FlashSpeed enum."""

    def test_flash_speed_values(self) -> None:
        """Test FlashSpeed enum values."""
        assert FlashSpeed.slow == 1
        assert FlashSpeed.medium == 2
        assert FlashSpeed.fast == 4

    def test_flash_speed_is_int(self) -> None:
        """Test that FlashSpeed values are integers."""
        assert isinstance(FlashSpeed.slow.value, int)
        assert isinstance(FlashSpeed.medium.value, int)
        assert isinstance(FlashSpeed.fast.value, int)


class TestBlynclightIntegration:
    """Integration tests for Blynclight."""

    def test_complete_workflow(self) -> None:
        """Test a complete workflow with multiple operations."""
        mock_hardware = create_mock_blynclight_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blynclight, "update"):
            # Only mock reset during initialization
            with patch.object(Blynclight, "reset"):
                blynclight = Blynclight(mock_hardware)

            # Test sequence of operations
            blynclight.dim()
            blynclight.flash((255, 0, 0), FlashSpeed.medium)

            # Mock super().reset() for the actual reset call
            with patch("busylight_core.vendors.embrava.blynclight.super"):
                blynclight.reset()

            # Verify final state after reset
            assert blynclight.state.off == 1
            assert blynclight.state.dim == 0
            assert blynclight.state.flash == 0

    def test_state_interactions(self) -> None:
        """Test interactions between different state settings."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update"),
        ):
            blynclight = Blynclight(mock_hardware)

            # Test flash and dim both set, then light turned off via on()
            blynclight.state.flash = True
            blynclight.state.dim = True
            blynclight.on((0, 0, 0))  # Turn off clears flash and dim

            assert blynclight.state.flash == 0
            assert blynclight.state.dim == 0


class TestBlynclightEdgeCases:
    """Test edge cases and error conditions."""

    def test_flash_with_none_speed(self) -> None:
        """Test flash method with None speed falls back to default."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update"),
        ):
            blynclight = Blynclight(mock_hardware)

            blynclight.flash((255, 255, 255), None)

            assert blynclight.state.speed == FlashSpeed.slow.value

    def test_bytes_with_specific_rgb_values(self) -> None:
        """Test __bytes__ method with specific RGB values."""
        mock_hardware = create_mock_blynclight_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blynclight, "reset"):
            blynclight = Blynclight(mock_hardware)

            # Set specific RGB values to test struct packing - this makes is_lit True
            blynclight.color = 255, 64, 128

            result = bytes(blynclight)

            # Verify the bytes contain the RGB values in the correct positions
            # struct format is "!xBBBBBBH" - skip first byte, then R,B,G...
            assert result[1] == 255  # Red
            assert result[2] == 128  # Blue
            assert result[3] == 64  # Green

    def test_multiple_device_ids_support(self) -> None:
        """Test that all supported device IDs work."""
        device_ids = [(0x2C0D, 0x0001), (0x2C0D, 0x000C), (0x0E53, 0x2516)]

        for vendor_id, product_id in device_ids:
            mock_hardware = Mock(spec=Hardware)
            mock_hardware.vendor_id = vendor_id
            mock_hardware.product_id = product_id
            mock_hardware.device_id = (vendor_id, product_id)
            mock_hardware.product_string = "Blynclight"

            result = Blynclight.claims(mock_hardware)
            assert result is True, (
                f"Failed to claim device {vendor_id:04X}:{product_id:04X}"
            )


class TestBlynclightStateRepr:
    """Test State class string representations."""

    def test_state_repr(self) -> None:
        """Test State.__repr__() method."""
        state = State()
        # Set state values to see in representation
        state.off = 1
        state.dim = 1
        state.flash = 1

        result = repr(state)

        # Should contain class name and hex representation
        assert "BlynclightState" in result
        assert "0x" in result
        assert result.startswith("BlynclightState(0x")
        assert result.endswith(")")

    def test_state_str(self) -> None:
        """Test State.__str__() method."""
        state = State()
        # Set some state values
        state.red = 0x01
        state.blue = 0x02
        state.green = 0x03
        state.off = 1
        state.dim = 1
        state.flash = 0
        state.speed = 2
        state.repeat = 1
        state.play = 0
        state.music = 5
        state.volume = 10
        state.mute = 1

        result = str(state)

        # Should contain all field values
        assert "red:    0x01" in result
        assert "blue:   0x02" in result
        assert "green:  0x03" in result
        assert "off:    1" in result
        assert "dim:    1" in result
        assert "flash:  0" in result
        assert "speed:  2" in result
        assert "repeat: 1" in result
        assert "play:   0" in result
        assert "music:  5" in result
        assert "volume: 10" in result
        assert "mute:   1" in result

        # Should be newline-separated
        lines = result.split("\n")
        assert len(lines) == 12


class TestBlynclightOnMethod:
    """Test the on() method coverage."""

    def test_on_method(self) -> None:
        """Test on() method sets color correctly."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update") as mock_update,
        ):
            blynclight = Blynclight(mock_hardware)
            test_color = (200, 100, 50)

            blynclight.on(test_color)

            assert blynclight.color == test_color
            mock_update.assert_called_once()

    def test_on_method_with_led_parameter(self) -> None:
        """Test on() method with led parameter (ignored for Blynclight)."""
        mock_hardware = create_mock_blynclight_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blynclight, "reset"),
            patch.object(Blynclight, "update") as mock_update,
        ):
            blynclight = Blynclight(mock_hardware)
            test_color = (150, 75, 25)

            blynclight.on(test_color, led=5)  # LED parameter should be ignored

            assert blynclight.color == test_color
            mock_update.assert_called_once()

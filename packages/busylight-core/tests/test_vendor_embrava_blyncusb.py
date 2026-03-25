"""Tests for the Embrava Blyncusb10 and Blyncusb20 devices."""

from unittest.mock import Mock, patch

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.embrava.blyncusb10 import Blyncusb10
from busylight_core.vendors.embrava.blyncusb20 import Blyncusb20
from busylight_core.vendors.embrava.implementation import (
    BlyncusbColor,
    rgb_to_blyncusb_color,
)


def create_mock_blyncusb10_hardware() -> Mock:
    """Create a properly configured mock hardware for Blyncusb10 device."""
    mock_hardware = Mock(spec=Hardware)
    mock_hardware.device_id = (0x1130, 0x0001)
    mock_hardware.device_type = ConnectionType.HID
    mock_hardware.path = b"/dev/hidraw0"
    mock_hardware.product_string = "Blynclight BLYNCUSB10"
    mock_hardware.vendor_id = 0x1130
    mock_hardware.product_id = 0x0001
    mock_hardware.interface_number = 1
    return mock_hardware


def create_mock_blyncusb20_hardware() -> Mock:
    """Create a properly configured mock hardware for Blyncusb20 device."""
    mock_hardware = Mock(spec=Hardware)
    mock_hardware.device_id = (0x1130, 0x1E00)
    mock_hardware.device_type = ConnectionType.HID
    mock_hardware.path = b"/dev/hidraw0"
    mock_hardware.product_string = "Blynclight BLYNCUSB20"
    mock_hardware.vendor_id = 0x1130
    mock_hardware.product_id = 0x1E00
    mock_hardware.interface_number = 1
    return mock_hardware


class TestBlyncusb10DeviceSupport:
    """Test Blyncusb10 device identification and support."""

    def test_supported_device_ids(self) -> None:
        """Verify Blyncusb10 includes expected device IDs."""
        assert isinstance(Blyncusb10.supported_device_ids, dict)
        assert (0x1130, 0x0001) in Blyncusb10.supported_device_ids
        assert (0x1130, 0x0002) in Blyncusb10.supported_device_ids

    def test_claims_correct_interface(self) -> None:
        """Verify claims succeeds for matching interface number."""
        mock_hardware = create_mock_blyncusb10_hardware()
        assert Blyncusb10.claims(mock_hardware) is True

    def test_claims_wrong_interface(self) -> None:
        """Verify claims fails for wrong interface number."""
        mock_hardware = create_mock_blyncusb10_hardware()
        mock_hardware.interface_number = 0
        assert Blyncusb10.claims(mock_hardware) is False

    def test_claims_wrong_device(self) -> None:
        """Verify claims fails for unrecognized device ID."""
        mock_hardware = Mock(spec=Hardware)
        mock_hardware.device_id = (0x1234, 0x5678)
        mock_hardware.interface_number = 1
        assert Blyncusb10.claims(mock_hardware) is False

    def test_vendor_name(self) -> None:
        """Verify vendor name is Embrava."""
        assert Blyncusb10.vendor() == "Embrava"


class TestBlyncusb10Behavior:
    """Test Blyncusb10 color and bytes behavior."""

    def test_bytes_conversion_red(self) -> None:
        """Verify bytes output for red matches expected protocol."""
        mock_hardware = create_mock_blyncusb10_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb10, "reset"):
            device = Blyncusb10(mock_hardware)
            device.color = (255, 0, 0)

            result = bytes(device)

            assert len(result) == 8
            assert result[:7] == bytes([0x55, 0x53, 0x42, 0x43, 0x00, 0x40, 0x02])
            assert result[7] == (BlyncusbColor.RED.value << 4) | 0x0F

    def test_bytes_conversion_off(self) -> None:
        """Verify bytes output for off/black."""
        mock_hardware = create_mock_blyncusb10_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb10, "reset"):
            device = Blyncusb10(mock_hardware)
            # Default color is (0, 0, 0) which maps to OFF

            result = bytes(device)

            assert result[7] == (BlyncusbColor.OFF.value << 4) | 0x0F

    def test_color_snaps_to_palette(self) -> None:
        """Verify setting an approximate color snaps to nearest palette entry."""
        mock_hardware = create_mock_blyncusb10_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb10, "reset"):
            device = Blyncusb10(mock_hardware)
            device.color = (200, 50, 50)

            # Should snap to pure red
            assert device.color == (255, 0, 0)

    def test_color_property(self) -> None:
        """Verify setting color stores the snapped palette RGB."""
        mock_hardware = create_mock_blyncusb10_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb10, "reset"):
            device = Blyncusb10(mock_hardware)
            device.color = (255, 0, 0)

            assert device.color == (255, 0, 0)

    def test_on_method(self) -> None:
        """Verify on() sets color and calls update."""
        mock_hardware = create_mock_blyncusb10_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blyncusb10, "reset"),
            patch.object(Blyncusb10, "update") as mock_update,
        ):
            device = Blyncusb10(mock_hardware)
            device.on((0, 255, 0))

            assert device.color == (0, 255, 0)
            mock_update.assert_called_once()

    def test_reset_method(self) -> None:
        """Verify reset() clears color to off."""
        mock_hardware = create_mock_blyncusb10_hardware()

        with patch.object(mock_hardware, "acquire"):
            with patch.object(Blyncusb10, "reset"):
                device = Blyncusb10(mock_hardware)

            device.color = (255, 0, 0)

            with patch.object(device, "update") as mock_update:
                device.reset()

            assert device.color == (0, 0, 0)
            mock_update.assert_called_once()

    def test_write_strategy(self) -> None:
        """Verify write strategy uses HID send_feature_report."""
        mock_hardware = create_mock_blyncusb10_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb10, "reset"):
            device = Blyncusb10(mock_hardware)
            assert device.write_strategy is mock_hardware.handle.send_feature_report


class TestBlyncusb20DeviceSupport:
    """Test Blyncusb20 device identification and support."""

    def test_supported_device_ids(self) -> None:
        """Verify Blyncusb20 includes expected device IDs."""
        assert isinstance(Blyncusb20.supported_device_ids, dict)
        assert (0x1130, 0x1E00) in Blyncusb20.supported_device_ids

    def test_claims_correct_interface(self) -> None:
        """Verify claims succeeds for matching interface number."""
        mock_hardware = create_mock_blyncusb20_hardware()
        assert Blyncusb20.claims(mock_hardware) is True

    def test_claims_wrong_interface(self) -> None:
        """Verify claims fails for wrong interface number."""
        mock_hardware = create_mock_blyncusb20_hardware()
        mock_hardware.interface_number = 0
        assert Blyncusb20.claims(mock_hardware) is False

    def test_vendor_name(self) -> None:
        """Verify vendor name is Embrava."""
        assert Blyncusb20.vendor() == "Embrava"


class TestBlyncusb20Behavior:
    """Test Blyncusb20 color and bytes behavior."""

    def test_bytes_conversion_red(self) -> None:
        """Verify bytes output for red matches expected TENX20 protocol."""
        mock_hardware = create_mock_blyncusb20_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb20, "reset"):
            device = Blyncusb20(mock_hardware)
            device.color = (255, 0, 0)

            result = bytes(device)

            assert len(result) == 65
            assert result[0] == 0x00
            assert result[1] == 0x60  # Tenx20Color.RED

    def test_bytes_conversion_off(self) -> None:
        """Verify bytes output for off/black."""
        mock_hardware = create_mock_blyncusb20_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb20, "reset"):
            device = Blyncusb20(mock_hardware)

            result = bytes(device)

            assert result[1] == 0x73  # Tenx20Color.OFF

    def test_write_strategy_two_step(self) -> None:
        """Verify Blyncusb20 write strategy sends reset then color."""
        mock_hardware = create_mock_blyncusb20_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb20, "reset"):
            device = Blyncusb20(mock_hardware)
            writer = device.write_strategy

            color_command = bytes([0x00, 0x60] + [0x00] * 63)
            writer(color_command)

            assert mock_hardware.handle.write.call_count == 2
            reset_call = mock_hardware.handle.write.call_args_list[0]
            assert reset_call[0][0][1] == 0x73  # RESET_CODE

    def test_color_snaps_to_palette(self) -> None:
        """Verify setting an approximate color snaps to nearest palette entry."""
        mock_hardware = create_mock_blyncusb20_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb20, "reset"):
            device = Blyncusb20(mock_hardware)
            device.color = (0, 0, 200)

            assert device.color == (0, 0, 255)

    def test_color_property(self) -> None:
        """Verify setting color stores the snapped palette RGB."""
        mock_hardware = create_mock_blyncusb20_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Blyncusb20, "reset"):
            device = Blyncusb20(mock_hardware)
            device.color = (0, 0, 255)

            assert device.color == (0, 0, 255)

    def test_on_method(self) -> None:
        """Verify on() sets color and calls update."""
        mock_hardware = create_mock_blyncusb20_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Blyncusb20, "reset"),
            patch.object(Blyncusb20, "update") as mock_update,
        ):
            device = Blyncusb20(mock_hardware)
            device.on((255, 255, 0))

            assert device.color == (255, 255, 0)
            mock_update.assert_called_once()

    def test_reset_method(self) -> None:
        """Verify reset() clears color to off."""
        mock_hardware = create_mock_blyncusb20_hardware()

        with patch.object(mock_hardware, "acquire"):
            with patch.object(Blyncusb20, "reset"):
                device = Blyncusb20(mock_hardware)

            device.color = (255, 0, 0)

            with patch.object(device, "update") as mock_update:
                device.reset()

            assert device.color == (0, 0, 0)
            mock_update.assert_called_once()


class TestRgbToBlyncusbColor:
    """Test the RGB-to-palette color mapping function."""

    def test_pure_red(self) -> None:
        """Verify pure red maps to RED."""
        assert rgb_to_blyncusb_color(255, 0, 0) == BlyncusbColor.RED

    def test_pure_green(self) -> None:
        """Verify pure green maps to GREEN."""
        assert rgb_to_blyncusb_color(0, 255, 0) == BlyncusbColor.GREEN

    def test_pure_blue(self) -> None:
        """Verify pure blue maps to BLUE."""
        assert rgb_to_blyncusb_color(0, 0, 255) == BlyncusbColor.BLUE

    def test_yellow(self) -> None:
        """Verify yellow maps to YELLOW."""
        assert rgb_to_blyncusb_color(255, 255, 0) == BlyncusbColor.YELLOW

    def test_cyan(self) -> None:
        """Verify cyan maps to CYAN."""
        assert rgb_to_blyncusb_color(0, 255, 255) == BlyncusbColor.CYAN

    def test_magenta(self) -> None:
        """Verify magenta maps to MAGENTA."""
        assert rgb_to_blyncusb_color(255, 0, 255) == BlyncusbColor.MAGENTA

    def test_white(self) -> None:
        """Verify white maps to WHITE."""
        assert rgb_to_blyncusb_color(255, 255, 255) == BlyncusbColor.WHITE

    def test_off_black(self) -> None:
        """Verify black maps to OFF."""
        assert rgb_to_blyncusb_color(0, 0, 0) == BlyncusbColor.OFF

    def test_off_near_black(self) -> None:
        """Verify near-black values map to OFF."""
        assert rgb_to_blyncusb_color(10, 10, 10) == BlyncusbColor.OFF

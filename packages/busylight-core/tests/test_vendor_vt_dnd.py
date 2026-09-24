"""Tests for VT DND Alpha and Omega devices."""

from unittest.mock import Mock, call, patch

import pytest

from busylight_core import VTDND, Light
from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.vt.implementation import State


@pytest.fixture
def mock_hardware() -> Hardware:
    """Create mocked VT HID hardware."""
    hardware = Mock(spec=Hardware)
    hardware.vendor_id = 0x340B
    hardware.product_id = 0xF001
    hardware.device_id = (0x340B, 0xF001)
    hardware.connection_type = ConnectionType.HID
    hardware.acquire = Mock()
    hardware.release = Mock()
    hardware.handle = Mock()
    hardware.handle.write = Mock(return_value=5)
    return hardware


@pytest.fixture
def light(mock_hardware: Hardware) -> VTDND:
    """Create a VT light that writes to mocked hardware."""
    device = VTDND(mock_hardware, reset=False, exclusive=False)
    device.__dict__["platform"] = "Windows"
    return device


class TestState:
    """Test VT command state serialization."""

    def test_default_state(self) -> None:
        """Initialize an empty five-byte report at brightness level two."""
        state = State()

        assert bytes(state) == b"\x00" * 5
        assert state.color == (0, 0, 0)
        assert state.brightness == 2

    def test_serializes_fields_in_protocol_order(self) -> None:
        """Serialize report, action, and RGB fields in big-endian order."""
        state = State()
        state.report = 0x01
        state.action = 0x04
        state.color = (0xFF, 0x80, 0x01)

        assert bytes(state) == bytes((0x01, 0x04, 0xFF, 0x80, 0x01))

    @pytest.mark.parametrize("brightness", [0, 4])
    def test_rejects_invalid_brightness(self, brightness: int) -> None:
        """Reject brightness values outside the supported range."""
        state = State()

        with pytest.raises(ValueError, match="between 1 and 3"):
            state.brightness = brightness


class TestVTDND:
    """Test public VT DND behavior with mocked HID transport."""

    def test_supported_devices_and_discovery(self) -> None:
        """Expose both device IDs and participate in light discovery."""
        assert VTDND.supported_device_ids == {
            (0x340B, 0xF001): "VT DND Omega",
            (0x340B, 0xF002): "VT DND Alpha",
        }
        assert VTDND.vendor() == "VT"
        assert VTDND in Light.subclasses()

    def test_color_property(self, light: VTDND) -> None:
        """Expose the current RGB command fields through color."""
        light.color = (10, 20, 30)

        assert light.color == (10, 20, 30)
        assert light.is_lit is True

    def test_on_writes_exact_windows_hid_report(self, light: VTDND) -> None:
        """Strip the generic Windows prefix before writing a VT report."""
        light.on((10, 20, 30))

        light.hardware.handle.write.assert_called_once_with(
            bytes((0x01, 0x04, 10, 20, 30))
        )

    def test_off_writes_off_command(self, light: VTDND) -> None:
        """Send the VT off action with empty data bytes."""
        light.off()

        light.hardware.handle.write.assert_called_once_with(
            bytes((0x01, 0x01, 0x00, 0x00, 0x00))
        )

    @pytest.mark.parametrize("color", [1, 2])
    def test_flash_accepts_supported_colors(self, light: VTDND, color: int) -> None:
        """Send either supported predefined flash color."""
        light.flash(color)  # type: ignore[arg-type]

        light.hardware.handle.write.assert_called_once_with(
            bytes((0x01, 0x02, color, 0x00, 0x00))
        )

    @pytest.mark.parametrize("color", [0, 3])
    def test_flash_rejects_unsupported_colors(self, light: VTDND, color: int) -> None:
        """Reject flash color identifiers outside one and two."""
        with pytest.raises(ValueError, match="must be 1 or 2"):
            light.flash(color)  # type: ignore[arg-type]

        light.hardware.handle.write.assert_not_called()

    def test_dim_sends_brightness_then_restores_color(self, light: VTDND) -> None:
        """Decrease brightness and resend the current color."""
        light.color = (10, 20, 30)

        with patch("busylight_core.vendors.vt.busylight.sleep") as mock_sleep:
            light.dim()

        assert light.state.brightness == 1
        assert light.color == (10, 20, 30)
        assert light.hardware.handle.write.call_args_list == [
            call(bytes((0x01, 0x09, 0x01, 0x00, 0x00))),
            call(bytes((0x01, 0x04, 10, 20, 30))),
        ]
        mock_sleep.assert_called_once_with(0.1)

    def test_dim_stops_at_one(self, light: VTDND) -> None:
        """Avoid writes when brightness is already one."""
        light.state.brightness = 1

        light.dim()

        assert light.state.brightness == 1
        light.hardware.handle.write.assert_not_called()

    def test_bright_sends_brightness_then_restores_color(self, light: VTDND) -> None:
        """Increase brightness and resend the current color."""
        light.color = (10, 20, 30)

        with patch("busylight_core.vendors.vt.busylight.sleep") as mock_sleep:
            light.bright()

        assert light.state.brightness == 3
        assert light.color == (10, 20, 30)
        assert light.hardware.handle.write.call_args_list == [
            call(bytes((0x01, 0x09, 0x03, 0x00, 0x00))),
            call(bytes((0x01, 0x04, 10, 20, 30))),
        ]
        mock_sleep.assert_called_once_with(0.1)

    def test_bright_stops_at_three(self, light: VTDND) -> None:
        """Avoid writes when brightness is already three."""
        light.state.brightness = 3

        light.bright()

        assert light.state.brightness == 3
        light.hardware.handle.write.assert_not_called()

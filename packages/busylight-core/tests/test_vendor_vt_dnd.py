"""Tests for VT DND Alpha and Omega devices."""

import asyncio
from unittest.mock import Mock, call, patch

import pytest

from busylight_core import DNDAlpha, DNDOmega, Light, VTLights
from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.mixins import ColorableMixin
from busylight_core.vendors.vt.dnd_base import DNDBase
from busylight_core.vendors.vt.implementation import (
    Action,
    Brightness,
    FlashMode,
    Report,
    State,
)

SET_BRIGHTNESS_LOW = bytes((0x01, 0x09, 0x01, 0x00, 0x00))
SET_BRIGHTNESS_HIGH = bytes((0x01, 0x09, 0x03, 0x00, 0x00))
SET_COLOR = bytes((0x01, 0x04, 10, 20, 30))
OFF = bytes((0x01, 0x01, 0x00, 0x00, 0x00))


@pytest.fixture
def mock_hardware() -> Hardware:
    """Create mocked VT DND Omega HID hardware."""
    hardware = Mock(spec=Hardware)
    hardware.vendor_id = 0x340B
    hardware.product_id = 0xF001
    hardware.device_id = (0x340B, 0xF001)
    hardware.connection_type = ConnectionType.HID
    hardware.handle = Mock()
    hardware.handle.write = Mock(return_value=5)
    return hardware


@pytest.fixture(params=["Windows", "Linux", "Darwin"])
def light(request: pytest.FixtureRequest, mock_hardware: Hardware) -> DNDOmega:
    """Create a DND Omega light on each supported platform."""
    device = DNDOmega(mock_hardware, reset=False, exclusive=False)
    device.__dict__["platform"] = request.param
    return device


def writes(light: DNDBase) -> list:
    """Return the payloads written to the light's hardware handle."""
    return light.hardware.handle.write.call_args_list


class TestState:
    """Test VT DND command report construction."""

    def test_default_state(self) -> None:
        """Initialize a five-byte report with only the report number set."""
        state = State()

        assert state.report == Report.ONE
        assert bytes(state) == bytes((0x01, 0x00, 0x00, 0x00, 0x00))

    def test_report_is_read_only(self) -> None:
        """Reject assignment to the fixed report number."""
        state = State()

        with pytest.raises(AttributeError, match="read only"):
            state.report = 2

    def test_command_serializes_in_protocol_order(self) -> None:
        """Serialize report, action, and data bytes in big-endian order."""
        state = State()
        state.command(Action.SetColor, (0xFF, 0x80, 0x01))

        assert state.report == Report.ONE
        assert bytes(state) == bytes((0x01, 0x04, 0xFF, 0x80, 0x01))

    def test_command_clears_previous_data(self) -> None:
        """Replace the previous command's data bytes."""
        state = State()
        state.set_color((1, 2, 3))
        state.off()

        assert state.data == (0, 0, 0)
        assert state.action == Action.Off

    @pytest.mark.parametrize(
        ("build", "expected"),
        [
            (lambda s: s.set_color((10, 20, 30)), SET_COLOR),
            (lambda s: s.set_brightness(Brightness.High), SET_BRIGHTNESS_HIGH),
            (lambda s: s.flash(FlashMode.TWO), bytes((0x01, 0x02, 0x02, 0, 0))),
            (lambda s: s.off(), OFF),
        ],
    )
    def test_command_builders(self, build, expected: bytes) -> None:
        """Build each command's exact report bytes."""
        state = State()
        build(state)

        assert bytes(state) == expected


class TestDNDDevices:
    """Test VT DND device classes and discovery."""

    def test_supported_device_ids(self) -> None:
        """Give each device its own class and device id."""
        assert DNDAlpha.supported_device_ids == {(0x340B, 0xF002): "DND Alpha"}
        assert DNDOmega.supported_device_ids == {(0x340B, 0xF001): "DND Omega"}

    @pytest.mark.parametrize("subclass", [DNDAlpha, DNDOmega])
    def test_class_hierarchy(self, subclass: type[DNDBase]) -> None:
        """Share the DND protocol and VT vendor identity."""
        assert issubclass(subclass, DNDBase)
        assert issubclass(subclass, ColorableMixin)
        assert subclass.vendor() == "VT"
        assert subclass in Light.subclasses()
        assert subclass in VTLights.subclasses()


class TestDNDBase:
    """Test VT DND behavior with mocked HID transport."""

    def test_on_writes_set_color(self, light: DNDOmega) -> None:
        """Write the exact report with no Windows prefix byte."""
        light.on((10, 20, 30))

        assert writes(light) == [call(SET_COLOR)]
        assert light.color == (10, 20, 30)
        assert light.is_lit

    def test_on_cancels_tasks(self, light: DNDOmega) -> None:
        """Cancel running effects before changing color."""
        with patch.object(light, "cancel_tasks") as mock_cancel:
            light.on((10, 20, 30))

        mock_cancel.assert_called_once()

    def test_off_writes_off_command(self, light: DNDOmega) -> None:
        """Send the dedicated off command and clear the color."""
        light.on((10, 20, 30))
        light.off()

        assert writes(light)[-1] == call(OFF)
        assert light.color == (0, 0, 0)
        assert not light.is_lit

    def test_on_black_writes_off_command(self, light: DNDOmega) -> None:
        """Send the dedicated off command instead of a black color."""
        light.on((0, 0, 0))

        assert writes(light) == [call(OFF)]
        assert not light.is_lit

    def test_off_cancels_tasks(self, light: DNDOmega) -> None:
        """Cancel running effects so they cannot relight the device."""
        with patch.object(light, "cancel_tasks") as mock_cancel:
            light.off()

        mock_cancel.assert_called_once()

    def test_reset_turns_off(self, light: DNDOmega) -> None:
        """Reset sends the off command."""
        light.reset()

        assert writes(light) == [call(OFF)]

    @pytest.mark.parametrize("mode", list(FlashMode))
    def test_flash_writes_mode(self, light: DNDOmega, mode: FlashMode) -> None:
        """Send the flash command without changing the tracked color."""
        light.on((10, 20, 30))
        light.flash(mode)

        assert writes(light)[-1] == call(bytes((0x01, 0x02, mode, 0x00, 0x00)))
        assert light.color == (10, 20, 30)

    def test_flash_defaults_to_mode_one(self, light: DNDOmega) -> None:
        """Use the first flash pattern when no mode is given."""
        light.flash()

        assert writes(light) == [call(bytes((0x01, 0x02, 0x01, 0x00, 0x00)))]

    @pytest.mark.parametrize("mode", [0, 3])
    def test_flash_rejects_unsupported_modes(self, light: DNDOmega, mode: int) -> None:
        """Reject flash modes the firmware does not define."""
        with pytest.raises(ValueError, match="FlashMode"):
            light.flash(mode)

        light.hardware.handle.write.assert_not_called()

    def test_brightness_defaults_to_medium(self, light: DNDOmega) -> None:
        """Assume the firmware's middle brightness level at startup."""
        assert light.brightness == Brightness.Medium

    @pytest.mark.parametrize(
        ("method", "level", "expected"),
        [
            ("dim", Brightness.Low, SET_BRIGHTNESS_LOW),
            ("bright", Brightness.High, SET_BRIGHTNESS_HIGH),
        ],
    )
    def test_brightness_change_resends_color(
        self,
        light: DNDOmega,
        method: str,
        level: Brightness,
        expected: bytes,
    ) -> None:
        """Send the brightness command, wait, then resend the color."""
        light.color = (10, 20, 30)

        with patch("busylight_core.vendors.vt.dnd_base.sleep") as mock_sleep:
            getattr(light, method)()

        assert light.brightness == level
        assert light.color == (10, 20, 30)
        assert writes(light) == [call(expected), call(SET_COLOR)]
        mock_sleep.assert_called_once_with(light.BRIGHTNESS_SETTLE_DELAY)

    @pytest.mark.parametrize(
        ("method", "level"),
        [("dim", Brightness.Low), ("bright", Brightness.High)],
    )
    def test_brightness_stops_at_limits(
        self,
        light: DNDOmega,
        method: str,
        level: Brightness,
    ) -> None:
        """Avoid writes when brightness is already at the limit."""
        light.brightness = level

        getattr(light, method)()

        assert light.brightness == level
        light.hardware.handle.write.assert_not_called()

    @pytest.mark.asyncio
    async def test_brightness_change_does_not_block_event_loop(
        self,
        mock_hardware: Hardware,
    ) -> None:
        """Resend the color from a task instead of sleeping in the event loop."""
        light = DNDOmega(mock_hardware, reset=False, exclusive=False)
        light.color = (10, 20, 30)

        with patch("busylight_core.vendors.vt.dnd_base.sleep") as mock_sleep:
            light.dim()

        mock_sleep.assert_not_called()
        assert writes(light)[-1] == call(SET_BRIGHTNESS_LOW)

        await light.tasks["restore_color"]

        assert writes(light)[-1] == call(SET_COLOR)

    @pytest.mark.asyncio
    async def test_off_cancels_pending_color_restore(
        self,
        mock_hardware: Hardware,
    ) -> None:
        """Keep the light off when turned off during a brightness change."""
        light = DNDOmega(mock_hardware, reset=False, exclusive=False)
        light.color = (10, 20, 30)
        light.dim()

        light.off()
        await asyncio.sleep(light.BRIGHTNESS_SETTLE_DELAY * 2)

        assert writes(light)[-1] == call(OFF)

    def test_write_strategy_is_cached(self, light: DNDOmega) -> None:
        """Build the write function once per light."""
        assert light.write_strategy is light.write_strategy

    @pytest.mark.asyncio
    async def test_flash_cancels_pending_color_restore(
        self,
        mock_hardware: Hardware,
    ) -> None:
        """Keep flashing when flash starts during a brightness change."""
        light = DNDOmega(mock_hardware, reset=False, exclusive=False)
        light.color = (10, 20, 30)
        light.dim()

        light.flash(FlashMode.ONE)
        await asyncio.sleep(light.BRIGHTNESS_SETTLE_DELAY * 2)

        assert writes(light)[-1] == call(bytes((0x01, 0x02, 0x01, 0x00, 0x00)))

"""Tests for Kuando BusylightBase shared functionality."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.mixins import ColorableMixin
from busylight_core.vendors.kuando import BusylightAlpha, BusylightOmega
from busylight_core.vendors.kuando.busylight_base import BusylightBase
from busylight_core.vendors.kuando.implementation import OpCode, Ring, State, Step
from busylight_core.vendors.kuando.kuando_base import KuandoBase


class TestKuandoBusylightStep:
    """Test the Step class for Kuando Busylight devices."""

    def test_step_initialization(self) -> None:
        """Test that Step initializes with correct default values."""
        step = Step()
        assert step.opcode == 0
        assert step.operand == 0
        assert step.body == 0
        assert step.color == (0, 0, 0)
        assert step.repeat == 0
        assert step.duty_cycle_on == 0
        assert step.duty_cycle_off == 0
        assert step.update == 0
        assert step.ringtone == 0
        assert step.volume == 0

    def test_step_keep_alive(self) -> None:
        """Test keep_alive method configuration."""
        step = Step()
        timeout = 10
        step.keep_alive(timeout)
        assert step.opcode == OpCode.KeepAlive
        assert step.operand == timeout
        assert step.body == 0

    def test_step_keep_alive_timeout_mask(self) -> None:
        """Test keep_alive method with timeout masking."""
        step = Step()
        timeout = 0x1F  # 31, should be masked to 0xF (15)
        step.keep_alive(timeout)
        assert step.opcode == OpCode.KeepAlive
        assert step.operand == 0xF  # Masked to 4 bits
        assert step.body == 0

    def test_step_boot(self) -> None:
        """Test boot method configuration."""
        step = Step()
        step.boot()
        assert step.opcode == OpCode.Boot
        assert step.operand == 0
        assert step.body == 0

    def test_step_reset(self) -> None:
        """Test reset method configuration."""
        step = Step()
        step.reset()
        assert step.opcode == OpCode.Reset
        assert step.operand == 0
        assert step.body == 0

    def test_step_jump_basic(self) -> None:
        """Test jump method with basic color."""
        step = Step()
        color = (255, 128, 64)
        step.jump(color)
        assert step.opcode == OpCode.Jump
        assert step.operand == 0  # default target
        # Color conversion has rounding - check approximately
        retrieved_color = step.color
        assert all(abs(retrieved_color[i] - color[i]) <= 2 for i in range(3))
        assert step.repeat == 0
        assert step.duty_cycle_on == 0
        assert step.duty_cycle_off == 0
        assert step.update == 0
        assert step.ringtone == Ring.Off
        assert step.volume == 0

    def test_step_jump_full_parameters(self) -> None:
        """Test jump method with all parameters."""
        step = Step()
        color = (200, 150, 100)
        target = 3
        repeat = 5
        on_time = 10
        off_time = 20
        update = 1
        ringtone = Ring.Buzz
        volume = 7

        step.jump(color, target, repeat, on_time, off_time, update, ringtone, volume)

        assert step.opcode == OpCode.Jump
        assert step.operand == target
        # Color conversion has rounding - check approximately
        retrieved_color = step.color
        assert all(
            abs(retrieved_color[i] - color[i]) <= 5 for i in range(3)
        )  # Allow larger tolerance
        assert step.repeat == repeat
        assert step.duty_cycle_on == on_time
        assert step.duty_cycle_off == off_time
        assert step.update == update
        assert step.ringtone == ringtone & 0xF  # Ringtone is masked to 4 bits
        assert step.volume == volume & 0x3  # Volume is masked to 3 bits

    def test_step_jump_parameter_masking(self) -> None:
        """Test jump method with parameter masking."""
        step = Step()
        color = (255, 255, 255)
        target = 0x1F  # Should be masked to 0xF
        repeat = 0x1FF  # Should be masked to 0xFF
        on_time = 0x1FF  # Should be masked to 0xFF
        off_time = 0x1FF  # Should be masked to 0xFF
        update = 0x3  # Should be masked to 0x1
        ringtone = 0x1F  # Should be masked to 0xF
        volume = 0x7  # Should be masked to 0x3

        step.jump(color, target, repeat, on_time, off_time, update, ringtone, volume)

        assert step.operand == 0xF
        assert step.repeat == 0xFF
        assert step.duty_cycle_on == 0xFF
        assert step.duty_cycle_off == 0xFF
        assert step.update == 0x1
        assert step.ringtone == 0xF
        assert step.volume == 0x3

    def test_step_color_property(self) -> None:
        """Test color property getter and setter."""
        step = Step()
        color = (128, 64, 32)
        step.color = color
        # Color conversion has rounding - check approximately
        retrieved_color = step.color
        assert all(abs(retrieved_color[i] - color[i]) <= 2 for i in range(3))

    def test_step_color_conversion(self) -> None:
        """Test color conversion from 0-255 to 0-100 range."""
        step = Step()
        # Test full range colors
        step.color = (255, 255, 255)
        # Colors should be converted and stored in 0-100 range internally
        # but retrieved as 0-255 range
        assert step.color == (255, 255, 255)

        step.color = (0, 0, 0)
        assert step.color == (0, 0, 0)

        # Test mid-range color
        step.color = (128, 128, 128)
        retrieved_color = step.color
        # Should be approximately 128 after conversion round-trip
        assert all(
            abs(c - 128) <= 2 for c in retrieved_color
        )  # Allow small rounding error


class TestKuandoBusylightState:
    """Test the State class for Kuando Busylight devices."""

    def test_state_initialization(self) -> None:
        """Test that State initializes with steps."""
        state = State()
        assert hasattr(state, "steps")
        assert len(state.steps) == 7  # State should have 7 steps
        for step in state.steps:
            assert isinstance(step, Step)
        assert hasattr(state, "footer")
        assert hasattr(state, "struct")


class TestKuandoBusylightBase:
    """Test the BusylightBase class shared functionality."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for testing."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x27BB
        hardware.product_id = 0x3BCA
        hardware.device_id = (0x27BB, 0x3BCA)
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def busylight(self, mock_hardware) -> BusylightBase:
        """Create a BusylightBase instance for testing."""
        # Mock the hardware handle methods
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=64)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 64)

        # Mock the claims method to allow instantiation
        with patch.object(BusylightBase, "claims", return_value=True):
            instance = BusylightBase(mock_hardware, reset=False, exclusive=False)

        # Mock the name property to avoid device_id lookup issues
        instance.name = "Test Busylight"
        return instance

    def test_state_property(self, busylight) -> None:
        """Test state property returns State instance."""
        assert isinstance(busylight.state, State)
        # Should be cached
        assert busylight.state is busylight.state

    def test_bytes_method(self, busylight) -> None:
        """Test __bytes__ method returns state bytes."""
        state_bytes = bytes(busylight)
        expected_bytes = bytes(busylight.state)
        assert state_bytes == expected_bytes
        assert (
            len(state_bytes) == 64
        )  # State should be 7 steps + 1 footer * 8 bytes each

    def test_on_method(self, busylight) -> None:
        """Test on() method with color."""
        color = (255, 128, 64)
        with (
            patch.object(busylight, "batch_update") as mock_batch,
            patch.object(busylight, "add_task") as mock_add_task,
        ):
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            busylight.on(color)

            assert busylight.color == color
            # Color conversion has rounding - check approximately
            retrieved_color = busylight.state.steps[0].color
            assert all(abs(retrieved_color[i] - color[i]) <= 2 for i in range(3))
            assert busylight.state.steps[0].opcode == OpCode.Jump
            mock_batch.assert_called_once()
            mock_add_task.assert_called_once_with(
                "keepalive", busylight.keepalive, interval=10
            )

    def test_off_method(self, busylight) -> None:
        """Test off() method."""
        # First turn on
        busylight.on((255, 0, 0))

        with (
            patch.object(busylight, "batch_update") as mock_batch,
            patch.object(busylight, "cancel_tasks") as mock_cancel_tasks,
        ):
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            busylight.off()

            assert busylight.color == (0, 0, 0)
            assert busylight.state.steps[0].color == (0, 0, 0)
            assert busylight.state.steps[0].opcode == OpCode.Jump
            mock_batch.assert_called_once()
            mock_cancel_tasks.assert_called_once()

    def test_on_method_with_led_parameter(self, busylight) -> None:
        """Test on() method with led parameter (should be ignored)."""
        color = (128, 255, 32)
        with (
            patch.object(busylight, "batch_update") as mock_batch,
            patch.object(busylight, "add_task") as mock_add_task,
        ):
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            busylight.on(color, led=5)  # LED parameter should be ignored

            assert busylight.color == color
            # Color conversion has rounding - check approximately
            retrieved_color = busylight.state.steps[0].color
            assert all(abs(retrieved_color[i] - color[i]) <= 2 for i in range(3))
            mock_batch.assert_called_once()
            mock_add_task.assert_called_once_with(
                "keepalive", busylight.keepalive, interval=10
            )

    def test_off_method_with_led_parameter(self, busylight) -> None:
        """Test off() method with led parameter (should be ignored)."""
        with (
            patch.object(busylight, "batch_update") as mock_batch,
            patch.object(busylight, "cancel_tasks") as mock_cancel_tasks,
        ):
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            busylight.off(led=3)  # LED parameter should be ignored

            assert busylight.color == (0, 0, 0)
            mock_batch.assert_called_once()
            mock_cancel_tasks.assert_called_once()

    def test_vendor_hierarchy(self, busylight) -> None:
        """Test BusylightBase inherits from KuandoBase properly."""
        # Test inheritance hierarchy
        assert isinstance(busylight, BusylightBase)
        assert isinstance(busylight, KuandoBase)
        assert isinstance(busylight, ColorableMixin)

        # Test class hierarchy
        assert issubclass(BusylightBase, KuandoBase)

        # Test vendor method comes from KuandoBase
        assert BusylightBase.vendor() == "Kuando"
        assert KuandoBase.vendor() == "Kuando"

    def test_method_resolution_order(self) -> None:
        """Test MRO follows expected pattern."""
        mro = BusylightBase.__mro__

        # Should be: BusylightBase -> ColorableMixin -> KuandoBase -> Light -> ...
        assert mro[0] == BusylightBase
        assert mro[1] == ColorableMixin
        assert mro[2].__name__ == "KuandoBase"
        assert mro[3].__name__ == "Light"

    def test_kuando_devices_inherit_from_base(self) -> None:
        """Test all Kuando devices inherit from KuandoBase."""
        kuando_devices = [BusylightBase, BusylightAlpha, BusylightOmega]

        for device_class in kuando_devices:
            assert issubclass(device_class, KuandoBase)
            assert device_class.vendor() == "Kuando"


class TestKuandoBusylightKeepAlive:
    """Test the keepalive functionality shared by all Kuando devices."""

    @pytest.fixture
    def mock_light(self) -> BusylightBase:
        """Create mock light for testing."""
        light = Mock(spec=BusylightBase)
        light.state = Mock()
        light.state.steps = [Mock(spec=Step) for _ in range(16)]
        light.batch_update = Mock()
        light.batch_update.return_value.__enter__ = Mock()
        light.batch_update.return_value.__exit__ = Mock()
        # Use the real keepalive method implementation
        light.keepalive = BusylightBase.keepalive.__get__(light, BusylightBase)
        light.KEEPALIVE_INTERVAL = BusylightBase.KEEPALIVE_INTERVAL
        return light

    def test_keepalive_(self, mock_light) -> None:
        """Test keepalive with default interval."""
        mock_light.keepalive()

        mock_light.state.steps[0].keep_alive.assert_called_with(
            mock_light.KEEPALIVE_INTERVAL
        )

        mock_light.batch_update.assert_called()

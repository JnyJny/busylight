"""Tests for ThingM Blink1 implementation."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.thingm import Blink1
from busylight_core.vendors.thingm.implementation import (
    LEDS,
    Action,
    ActionField,
    BlueField,
    CountField,
    FadeField,
    GreenField,
    LedsField,
    LinesField,
    PlayField,
    RedField,
    Report,
    ReportField,
    StartField,
    State,
    StopField,
)
from busylight_core.vendors.thingm.thingm_base import ThingMBase


class TestThingMBlink1Fields:
    """Test the bit field classes."""

    def test_field_positions(self) -> None:
        """Test bit field positions and widths."""
        # Test bit field positions
        assert ReportField().field == slice(56, 64)
        assert ActionField().field == slice(48, 56)
        assert RedField().field == slice(40, 48)
        assert GreenField().field == slice(32, 40)
        assert BlueField().field == slice(24, 32)
        assert PlayField().field == slice(40, 48)  # alias for red
        assert StartField().field == slice(32, 40)  # alias for green
        assert StopField().field == slice(24, 32)  # alias for blue
        assert CountField().field == slice(16, 24)
        assert FadeField().field == slice(8, 24)  # 16-bit field
        assert LedsField().field == slice(0, 8)
        assert LinesField().field == slice(0, 8)  # alias for leds


class TestThingMBlink1Enums:
    """Test the enum classes."""

    def test_action_enum_values(self) -> None:
        """Test Action enum has correct character values."""
        assert Action.FadeColor == ord("c")
        assert Action.SetColor == ord("n")
        assert Action.ReadColor == ord("r")
        assert Action.ServerTickle == ord("D")
        assert Action.PlayLoop == ord("p")
        assert Action.PlayStateRead == ord("S")
        assert Action.SetColorPattern == ord("P")
        assert Action.SaveColorPatterns == ord("W")
        assert Action.ReadColorPattern == ord("R")
        assert Action.SetLEDn == ord("l")
        assert Action.ReadEEPROM == ord("e")
        assert Action.WriteEEPROM == ord("E")
        assert Action.GetVersion == ord("v")
        assert Action.TestCommand == ord("!")
        assert Action.WriteNote == ord("F")
        assert Action.ReadNote == ord("f")
        assert Action.Bootloader == ord("G")
        assert Action.LockBootLoader == ord("L")
        assert Action.SetStartupParams == ord("B")
        assert Action.GetStartupParams == ord("b")
        assert Action.ServerModeTickle == ord("D")
        assert Action.GetChipID == ord("U")

    def test_leds_enum_values(self) -> None:
        """Test LEDS enum values."""
        assert LEDS.All == 0
        assert LEDS.Top == 1
        assert LEDS.Bottom == 2

    def test_report_enum_values(self) -> None:
        """Test Report enum values."""
        assert Report.One == 1
        assert Report.Two == 2


class TestThingMBlink1State:
    """Test the State class."""

    def test_state_initialization(self) -> None:
        """Test State initializes with correct default values."""
        state = State()
        assert state.report == 0
        assert state.action == 0
        assert state.red == 0
        assert state.green == 0
        assert state.blue == 0
        assert state.play == 0
        assert state.start == 0
        assert state.stop == 0
        assert state.count == 0
        assert state.fade == 0
        assert state.leds == 0
        assert state.line == 0
        assert state.color == (0, 0, 0)

    def test_state_color_property(self) -> None:
        """Test color property getter and setter."""
        state = State()
        color = (255, 128, 64)
        state.color = color
        assert state.color == color
        assert state.red == 255
        assert state.green == 128
        assert state.blue == 64

    def test_state_alias_fields(self) -> None:
        """Test that alias fields work correctly."""
        state = State()

        # Test play/red alias
        state.play = 100
        assert state.red == 100

        state.red = 200
        assert state.play == 200

        # Test start/green alias
        state.start = 150
        assert state.green == 150

        state.green = 250
        assert state.start == 250

        # Test stop/blue alias
        state.stop = 75
        assert state.blue == 75

        state.blue = 175
        assert state.stop == 175

        # Test line/leds alias
        state.line = 5
        assert state.leds == 5

        state.leds = 7
        assert state.line == 7

    def test_state_fade_to_color_default(self) -> None:
        """Test fade_to_color with default parameters."""
        state = State()
        color = (255, 128, 64)
        state.fade_to_color(color)

        assert state.report == Report.One
        assert state.action == Action.FadeColor
        assert state.color == color
        assert state.fade == 10  # default fade_ms
        assert state.leds == LEDS.All  # default leds

    def test_state_fade_to_color_custom(self) -> None:
        """Test fade_to_color with custom parameters."""
        state = State()
        color = (200, 100, 50)
        fade_ms = 500
        leds = LEDS.Top

        state.fade_to_color(color, fade_ms, leds)

        assert state.report == Report.One
        assert state.action == Action.FadeColor
        assert state.color == color
        assert state.fade == fade_ms
        assert state.leds == leds

    def test_state_fade_to_color_clears_previous(self) -> None:
        """Test fade_to_color clears previous state."""
        state = State()
        # Set some initial values
        state.count = 5
        state.play = 10
        state.start = 15
        state.stop = 20

        state.fade_to_color((0, 0, 0))  # Use black to avoid alias conflicts

        # Should be cleared
        assert state.count == 0
        assert state.play == 0  # red should be 0
        assert state.start == 0  # green should be 0
        assert state.stop == 0  # blue should be 0

    def test_state_write_pattern_line(self) -> None:
        """Test write_pattern_line method."""
        state = State()
        color = (128, 64, 32)
        fade_ms = 1000
        index = 5

        state.write_pattern_line(color, fade_ms, index)

        assert state.report == Report.One
        assert state.action == Action.SetColorPattern
        assert state.color == color
        assert state.fade == fade_ms
        assert state.line == index

    def test_state_save_patterns(self) -> None:
        """Test save_patterns method."""
        state = State()
        state.save_patterns()

        assert state.report == Report.One
        assert state.action == Action.SaveColorPatterns
        assert state.color == (0xBE, 0xEF, 0xCA)
        assert state.count == 0xFE

    def test_state_play_loop_default(self) -> None:
        """Test play_loop with default parameters."""
        state = State()
        play = 1
        start = 0
        stop = 5

        state.play_loop(play, start, stop)

        assert state.report == Report.One
        assert state.action == Action.PlayLoop
        assert state.play == play
        assert state.start == start
        assert state.stop == stop
        assert state.count == 0  # default count

    def test_state_play_loop_custom(self) -> None:
        """Test play_loop with custom parameters."""
        state = State()
        play = 2
        start = 1
        stop = 10
        count = 3

        state.play_loop(play, start, stop, count)

        assert state.report == Report.One
        assert state.action == Action.PlayLoop
        assert state.play == play
        assert state.start == start
        assert state.stop == stop
        assert state.count == count

    def test_state_clear_patterns_default(self) -> None:
        """Test clear_patterns with default parameters."""
        state = State()

        with patch.object(state, "write_pattern_line") as mock_write:
            state.clear_patterns()

            # Should call write_pattern_line for indices 0-15
            assert mock_write.call_count == 16
            for i in range(16):
                mock_write.assert_any_call((0, 0, 0), 0, i)

    def test_state_clear_patterns_custom(self) -> None:
        """Test clear_patterns with custom parameters."""
        state = State()
        start = 5
        count = 3

        with patch.object(state, "write_pattern_line") as mock_write:
            state.clear_patterns(start, count)

            # Should call write_pattern_line for indices 5-7
            assert mock_write.call_count == 3
            for i in range(start, start + count):
                mock_write.assert_any_call((0, 0, 0), 0, i)

    def test_state_methods_clear_previous(self) -> None:
        """Test that all state methods clear previous state."""
        state = State()

        # Set some initial values
        state.report = Report.Two
        state.action = Action.ReadColor
        state.color = (100, 100, 100)
        state.fade = 100
        state.leds = LEDS.Bottom
        state.count = 10

        # Each method should clear state
        methods_to_test = [
            lambda: state.fade_to_color((255, 0, 0)),
            lambda: state.write_pattern_line((0, 255, 0), 500, 3),
            lambda: state.save_patterns(),
            lambda: state.play_loop(1, 0, 5),
        ]

        for method in methods_to_test:
            # Set some values first
            state.fade = 999
            state.count = 999

            # Call method
            method()

            # Should have cleared and set new values
            assert state.report == Report.One
            assert state.action in [
                Action.FadeColor,
                Action.SetColorPattern,
                Action.SaveColorPatterns,
                Action.PlayLoop,
            ]


class TestThingMBlink1:
    """Test the main Blink1 class."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for testing."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x27B8
        hardware.product_id = 0x01ED
        hardware.device_id = (0x27B8, 0x01ED)
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def blink1(self, mock_hardware) -> Blink1:
        """Create a Blink1 instance for testing."""
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=8)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 8)
        mock_hardware.handle.send_feature_report = Mock(return_value=8)
        return Blink1(mock_hardware, reset=False, exclusive=False)

    def test_vendor_method(self) -> None:
        """Test vendor() method returns correct vendor name."""
        assert Blink1.vendor() == "ThingM"

    def test_supported_device_ids(self) -> None:
        """Test supported_device_ids contains expected devices."""
        device_ids = Blink1.supported_device_ids
        assert (0x27B8, 0x01ED) in device_ids
        assert device_ids[(0x27B8, 0x01ED)] == "Blink(1)"

    def test_state_property(self, blink1) -> None:
        """Test state property returns State instance."""
        assert isinstance(blink1.state, State)
        # Should be cached
        assert blink1.state is blink1.state

    def test_bytes_method(self, blink1) -> None:
        """Test __bytes__ method returns state bytes."""
        state_bytes = bytes(blink1)
        expected_bytes = bytes(blink1.state)
        assert state_bytes == expected_bytes
        assert len(state_bytes) == 8  # State should be 64 bits / 8 = 8 bytes

    def test_write_strategy_property(self, blink1) -> None:
        """Test write_strategy property returns send_feature_report."""
        strategy = blink1.write_strategy
        assert strategy == blink1.hardware.handle.send_feature_report

    def test_on_method_default_led(self, blink1) -> None:
        """Test on() method with default LED."""
        color = (255, 128, 64)
        with patch.object(blink1, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blink1.on(color)

            assert blink1.color == color
            assert blink1.state.color == color
            assert blink1.state.action == Action.FadeColor
            assert blink1.state.leds == LEDS.All  # Default LED
            mock_batch.assert_called_once()

    def test_on_method_specific_led(self, blink1) -> None:
        """Test on() method with specific LED."""
        color = (200, 100, 50)
        led = 1
        with patch.object(blink1, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blink1.on(color, led=led)

            assert blink1.color == color
            assert blink1.state.color == color
            assert blink1.state.action == Action.FadeColor
            assert blink1.state.leds == LEDS.Top  # LED 1
            mock_batch.assert_called_once()

    def test_on_method_led_mapping(self, blink1) -> None:
        """Test on() method LED mapping."""
        color = (100, 100, 100)
        test_cases = [
            (0, LEDS.All),
            (1, LEDS.Top),
            (2, LEDS.Bottom),
        ]

        for led_num, expected_leds in test_cases:
            with patch.object(blink1, "batch_update") as mock_batch:
                mock_batch.return_value.__enter__ = Mock()
                mock_batch.return_value.__exit__ = Mock()

                blink1.on(color, led=led_num)

                assert blink1.state.leds == expected_leds

    def test_on_method_batch_update_usage(self, blink1) -> None:
        """Test on() method uses batch_update correctly."""
        color = (150, 75, 25)
        with patch.object(blink1, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blink1.on(color)

            mock_batch.assert_called_once()
            mock_batch.return_value.__enter__.assert_called_once()
            mock_batch.return_value.__exit__.assert_called_once()

    def test_on_method_state_configuration(self, blink1) -> None:
        """Test on() method configures state correctly."""
        color = (255, 0, 255)
        with patch.object(blink1, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            blink1.on(color, led=2)

            # Check that state is properly configured
            assert blink1.state.report == Report.One
            assert blink1.state.action == Action.FadeColor
            assert blink1.state.color == color
            assert blink1.state.fade == 10  # Default fade
            assert blink1.state.leds == LEDS.Bottom

    def test_bytes_integration(self, blink1) -> None:
        """Test integration between on() method and bytes() output."""
        color = (128, 64, 32)
        blink1.on(color, led=1)

        # Get bytes
        result = bytes(blink1)

        # Should have proper configuration
        assert blink1.state.color == color
        assert blink1.state.leds == LEDS.Top
        assert len(result) == 8

    def test_state_persistence(self, blink1) -> None:
        """Test that state persists across operations."""
        color = (200, 150, 100)
        blink1.on(color)

        # State should persist
        assert blink1.state.color == color
        assert blink1.state.action == Action.FadeColor

        # bytes() should return consistent results
        result1 = bytes(blink1)
        result2 = bytes(blink1)
        assert result1 == result2

    def test_write_strategy_integration(self, blink1) -> None:
        """Test write_strategy integration with hardware."""
        strategy = blink1.write_strategy
        assert callable(strategy)
        assert strategy == blink1.hardware.handle.send_feature_report

        # Should be able to call it
        test_data = [1, 2, 3, 4, 5, 6, 7, 8]
        strategy(test_data)
        blink1.hardware.handle.send_feature_report.assert_called_once_with(test_data)

    def test_leds_enum_usage(self, blink1) -> None:
        """Test that LEDS enum is properly used."""
        color = (255, 255, 255)

        # Test different LED values
        for led_value in [0, 1, 2]:
            with patch.object(blink1, "batch_update") as mock_batch:
                mock_batch.return_value.__enter__ = Mock()
                mock_batch.return_value.__exit__ = Mock()

                blink1.on(color, led=led_value)

                # Should convert to proper LEDS enum
                assert isinstance(blink1.state.leds, int)
                assert blink1.state.leds == LEDS(led_value)

    def test_color_and_led_independence(self, blink1) -> None:
        """Test that color and LED settings are independent."""
        color1 = (255, 0, 0)
        color2 = (0, 255, 0)

        with patch.object(blink1, "batch_update") as mock_batch:
            mock_batch.return_value.__enter__ = Mock()
            mock_batch.return_value.__exit__ = Mock()

            # Set first color with LED 1
            blink1.on(color1, led=1)
            assert blink1.state.color == color1
            assert blink1.state.leds == LEDS.Top

            # Set second color with LED 2
            blink1.on(color2, led=2)
            assert blink1.state.color == color2
            assert blink1.state.leds == LEDS.Bottom

    def test_state_word_size(self, blink1) -> None:
        """Test that state word is correct size."""
        # State should be 64 bits
        assert len(bytes(blink1.state)) == 8

        # After configuration, should still be 8 bytes
        blink1.on((255, 128, 64))
        assert len(bytes(blink1.state)) == 8

    def test_vendor_hierarchy(self, blink1) -> None:
        """Test Blink1 inherits from ThingMBase properly."""
        # Test inheritance hierarchy
        assert isinstance(blink1, Blink1)
        assert isinstance(blink1, ThingMBase)

        # Test class hierarchy
        assert issubclass(Blink1, ThingMBase)

        # Test vendor method comes from ThingMBase
        assert Blink1.vendor() == "ThingM"
        assert ThingMBase.vendor() == "ThingM"

    def test_method_resolution_order(self) -> None:
        """Test MRO follows expected pattern."""
        mro = Blink1.__mro__

        # Should be: Blink1 -> ThingMBase -> Light -> ...
        assert mro[0] == Blink1
        assert mro[1].__name__ == "ThingMBase"
        assert mro[2].__name__ == "Light"

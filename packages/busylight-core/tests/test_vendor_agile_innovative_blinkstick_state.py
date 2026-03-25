"""Tests for Agile Innovative BlinkStick State implementation."""

from busylight_core.vendors.agile_innovative.implementation import State


class TestBlinkStickState:
    """Test the BlinkStick State class."""

    def test_state_initialization(self) -> None:
        """Test State initializes with correct parameters."""
        state = State(report=1, nleds=8)
        assert state.report == 1
        assert state.nleds == 8
        assert state.channel == 0
        assert state.colors == [(0, 0, 0)] * 8

    def test_state_blinkstick_factory(self) -> None:
        """Test blinkstick() factory method."""
        state = State.blinkstick()
        assert state.report == 1
        assert state.nleds == 1
        assert state.channel == 0
        assert state.colors == [(0, 0, 0)] * 1

    def test_state_blinkstick_pro_factory(self) -> None:
        """Test blinkstick_pro() factory method."""
        state = State.blinkstick_pro()
        assert state.report == 2
        assert state.nleds == 192
        assert state.channel == 0
        assert state.colors == [(0, 0, 0)] * 192

    def test_state_blinkstick_square_factory(self) -> None:
        """Test blinkstick_square() factory method."""
        state = State.blinkstick_square()
        assert state.report == 6
        assert state.nleds == 8
        assert state.channel == 0
        assert state.colors == [(0, 0, 0)] * 8

    def test_state_blinkstick_strip_factory(self) -> None:
        """Test blinkstick_strip() factory method."""
        state = State.blinkstick_strip()
        assert state.report == 6
        assert state.nleds == 8
        assert state.channel == 0
        assert state.colors == [(0, 0, 0)] * 8

    def test_state_blinkstick_nano_factory(self) -> None:
        """Test blinkstick_nano() factory method."""
        state = State.blinkstick_nano()
        assert state.report == 6
        assert state.nleds == 2
        assert state.channel == 0
        assert state.colors == [(0, 0, 0)] * 2

    def test_state_blinkstick_flex_factory(self) -> None:
        """Test blinkstick_flex() factory method."""
        state = State.blinkstick_flex()
        assert state.report == 6
        assert state.nleds == 32
        assert state.channel == 0
        assert state.colors == [(0, 0, 0)] * 32

    def test_state_color_property_getter_empty(self) -> None:
        """Test color property getter with empty colors."""
        state = State(report=1, nleds=4)
        assert state.color == (0, 0, 0)

    def test_state_color_property_getter_with_colors(self) -> None:
        """Test color property getter with colors set."""
        state = State(report=1, nleds=4)
        # Set colors in GRB format internally
        state.colors = [(0, 0, 0), (128, 255, 64), (0, 0, 0), (0, 0, 0)]
        # Should return first non-zero color converted to RGB
        assert state.color == (255, 128, 64)  # GRB (128, 255, 64) -> RGB (255, 128, 64)

    def test_state_color_property_getter_all_zero(self) -> None:
        """Test color property getter with all zero colors."""
        state = State(report=1, nleds=4)
        state.colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]
        assert state.color == (0, 0, 0)

    def test_state_color_property_setter(self) -> None:
        """Test color property setter converts RGB to GRB."""
        state = State(report=1, nleds=4)
        state.color = (255, 128, 64)  # RGB
        # Should be converted to GRB and set for all LEDs
        expected_grb = (128, 255, 64)  # GRB format
        assert state.colors == [expected_grb, expected_grb, expected_grb, expected_grb]

    def test_state_get_led_valid_index(self) -> None:
        """Test get_led() with valid index."""
        state = State(report=1, nleds=4)
        state.colors = [(128, 255, 64), (0, 128, 255), (255, 0, 128), (64, 32, 16)]
        # Should return RGB format (converted from internal GRB)
        assert state.get_led(0) == (
            255,
            128,
            64,
        )  # GRB (128, 255, 64) -> RGB (255, 128, 64)
        assert state.get_led(1) == (
            128,
            0,
            255,
        )  # GRB (0, 128, 255) -> RGB (128, 0, 255)
        assert state.get_led(2) == (
            0,
            255,
            128,
        )  # GRB (255, 0, 128) -> RGB (0, 255, 128)
        assert state.get_led(3) == (32, 64, 16)  # GRB (64, 32, 16) -> RGB (32, 64, 16)

    def test_state_get_led_invalid_index(self) -> None:
        """Test get_led() with invalid index returns (0, 0, 0)."""
        state = State(report=1, nleds=4)
        state.colors = [(128, 255, 64), (0, 128, 255)]
        assert state.get_led(5) == (0, 0, 0)  # Index out of range
        assert state.get_led(10) == (0, 0, 0)  # Index out of range

    def test_state_set_led_valid_index(self) -> None:
        """Test set_led() with valid index."""
        state = State(report=1, nleds=4)
        state.colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]
        state.set_led(1, (255, 128, 64))  # RGB input
        # Should be converted to GRB and set at index 1
        expected_grb = (128, 255, 64)
        assert state.colors[1] == expected_grb
        assert state.colors[0] == (0, 0, 0)  # Other LEDs unchanged
        assert state.colors[2] == (0, 0, 0)
        assert state.colors[3] == (0, 0, 0)

    def test_state_set_led_invalid_index(self) -> None:
        """Test set_led() with invalid index (should be suppressed)."""
        state = State(report=1, nleds=2)
        # Should not raise IndexError due to contextlib.suppress
        state.set_led(5, (255, 128, 64))
        # Colors should remain unchanged
        assert state.colors == [(0, 0, 0), (0, 0, 0)]

    def test_state_bytes_empty(self) -> None:
        """Test __bytes__() with empty colors."""
        state = State(report=1, nleds=4)
        result = bytes(state)
        # [report, channel] + 4 empty RGB tuples
        expected = bytes([1, 0] + [0, 0, 0] * 4)
        assert result == expected

    def test_state_bytes_with_colors(self) -> None:
        """Test __bytes__() with colors set."""
        state = State(report=6, nleds=3)
        state.colors = [(128, 255, 64), (0, 128, 255), (255, 0, 128)]
        result = bytes(state)
        expected = bytes(
            [6, 0, 128, 255, 64, 0, 128, 255, 255, 0, 128]
        )  # [report, channel] + colors
        assert result == expected

    def test_state_bytes_single_led(self) -> None:
        """Test __bytes__() with single LED."""
        state = State(report=1, nleds=1)
        state.colors = [(100, 200, 50)]
        result = bytes(state)
        expected = bytes([1, 0, 100, 200, 50])  # [report, channel] + single color
        assert result == expected

    def test_state_rgb_grb_conversion_consistency(self) -> None:
        """Test RGB to GRB conversion consistency."""
        state = State(report=1, nleds=1)
        rgb_color = (255, 128, 64)
        state.color = rgb_color
        retrieved_color = state.color
        assert retrieved_color == rgb_color

    def test_state_multiple_led_operations(self) -> None:
        """Test operations with multiple LEDs."""
        state = State(report=6, nleds=4)
        # Initialize colors array first
        state.colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]

        # Set individual LEDs
        state.set_led(0, (255, 0, 0))  # Red -> stored as (0, 255, 0) in GRB
        state.set_led(1, (0, 255, 0))  # Green -> stored as (255, 0, 0) in GRB
        state.set_led(2, (0, 0, 255))  # Blue -> stored as (0, 0, 255) in GRB
        state.set_led(3, (255, 255, 0))  # Yellow -> stored as (255, 255, 0) in GRB

        # Verify individual LEDs (returned in RGB format, converted from internal GRB)
        assert state.get_led(0) == (255, 0, 0)  # RGB format
        assert state.get_led(1) == (0, 255, 0)  # RGB format
        assert state.get_led(2) == (0, 0, 255)  # RGB format
        assert state.get_led(3) == (255, 255, 0)  # RGB format

        # Verify color property returns first non-zero converted to RGB
        assert state.color == (255, 0, 0)  # First LED returns RGB

    def test_state_color_property_overrides_individual_leds(self) -> None:
        """Test that setting color property overrides individual LED colors."""
        state = State(report=1, nleds=4)
        # Set individual LEDs first
        state.set_led(0, (255, 0, 0))
        state.set_led(1, (0, 255, 0))
        state.set_led(2, (0, 0, 255))
        state.set_led(3, (255, 255, 0))

        # Set color property - should override all
        state.color = (128, 64, 32)
        expected_grb = (64, 128, 32)
        assert state.colors == [expected_grb, expected_grb, expected_grb, expected_grb]

    def test_state_rgb_to_grb_conversion(self) -> None:
        """Test rgb_to_grb() static method."""
        # Test various RGB colors
        assert State.rgb_to_grb((255, 128, 64)) == (128, 255, 64)  # RGB -> GRB
        assert State.rgb_to_grb((0, 255, 0)) == (255, 0, 0)  # Green -> GRB
        assert State.rgb_to_grb((255, 0, 0)) == (0, 255, 0)  # Red -> GRB
        assert State.rgb_to_grb((0, 0, 255)) == (0, 0, 255)  # Blue -> GRB
        assert State.rgb_to_grb((255, 255, 255)) == (255, 255, 255)  # White -> GRB
        assert State.rgb_to_grb((0, 0, 0)) == (0, 0, 0)  # Black -> GRB

    def test_state_grb_to_rgb_conversion(self) -> None:
        """Test grb_to_rgb() static method."""
        # Test various GRB colors
        assert State.grb_to_rgb((128, 255, 64)) == (255, 128, 64)  # GRB -> RGB
        assert State.grb_to_rgb((255, 0, 0)) == (0, 255, 0)  # GRB -> Green
        assert State.grb_to_rgb((0, 255, 0)) == (255, 0, 0)  # GRB -> Red
        assert State.grb_to_rgb((0, 0, 255)) == (0, 0, 255)  # GRB -> Blue
        assert State.grb_to_rgb((255, 255, 255)) == (255, 255, 255)  # GRB -> White
        assert State.grb_to_rgb((0, 0, 0)) == (0, 0, 0)  # GRB -> Black

    def test_state_color_conversion_roundtrip(self) -> None:
        """Test that RGB -> GRB -> RGB conversion is consistent."""
        test_colors = [
            (255, 128, 64),
            (0, 255, 0),
            (255, 0, 0),
            (0, 0, 255),
            (255, 255, 255),
            (0, 0, 0),
            (128, 64, 192),
        ]

        for rgb_color in test_colors:
            grb_color = State.rgb_to_grb(rgb_color)
            converted_back = State.grb_to_rgb(grb_color)
            assert converted_back == rgb_color

"""Tests for the simplified controller."""

from unittest.mock import Mock, patch

import pytest
from busylight.controller import LightController, LightSelection


class MockLight:
    def __init__(self, name: str):
        self.name = name
        self.is_on = False
        self.current_color = None
        self.current_led = 0
        self.tasks = {}
        self.add_task = Mock(return_value=Mock())
        self.cancel_tasks = Mock()
        self.release = Mock()

    def on(self, color, led=0):
        self.is_on = True
        self.current_color = color
        self.current_led = led

    def off(self):
        self.is_on = False
        self.current_color = None

    def __lt__(self, other):
        return self.name < other.name

    def __le__(self, other):
        return self.name <= other.name

    def __gt__(self, other):
        return self.name > other.name

    def __ge__(self, other):
        return self.name >= other.name

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash(id(self))


class TestLightSelection:
    def test_basic_operations(self):
        lights = [MockLight("Test")]
        selection = LightSelection(lights)

        assert len(selection) == 1
        assert bool(selection) is True
        assert list(selection) == lights

    def test_turn_off(self):
        lights = [MockLight("Test")]
        selection = LightSelection(lights)

        selection.turn_off()
        assert not lights[0].is_on

    def test_apply_effect_calls_asyncio_run(self):
        lights = [MockLight("Test")]
        selection = LightSelection(lights)

        mock_effect = Mock()
        mock_effect.name = "test_effect"
        mock_effect.priority = 1
        mock_effect.default_interval = 0.5
        mock_effect.count = 1

        # Test that asyncio.run is called when no event loop is running
        with (
            patch("busylight.controller.asyncio.run") as mock_run,
            patch(
                "busylight.controller.asyncio.get_running_loop",
                side_effect=RuntimeError,
            ),
        ):
            selection.apply_effect(mock_effect)
            mock_run.assert_called_once()

    def test_turn_on_with_color_tuple(self):
        lights = [MockLight("Test")]
        selection = LightSelection(lights)

        selection.turn_on((255, 128, 0))  # Orange color

        # Verify the light was turned on with correct color
        assert lights[0].is_on
        assert lights[0].current_color == (255, 128, 0)

    def test_blink_calls_apply_effect(self):
        lights = [MockLight("Test")]
        selection = LightSelection(lights)

        # Test that blink calls apply_effect by mocking it
        with patch.object(selection, "apply_effect") as mock_apply_effect:
            selection.blink((0, 255, 0), count=3, speed="fast")
            mock_apply_effect.assert_called_once()


class TestLightController:
    def test_init(self):
        controller = LightController()
        assert controller.light_class is not None

    def test_no_lights(self):
        mock_light_class = Mock()
        mock_light_class.all_lights.return_value = []

        controller = LightController(mock_light_class)
        assert len(controller) == 0
        assert not bool(controller)

    def test_fluent_selection(self):
        mock_lights = [MockLight("Light1"), MockLight("Light2")]
        mock_light_class = Mock()
        mock_light_class.all_lights.return_value = mock_lights

        controller = LightController(mock_light_class)

        all_selection = controller.all()
        assert len(all_selection) == 2

        first_selection = controller.first()
        assert len(first_selection) == 1

        by_index_selection = controller.by_index(0)
        assert len(by_index_selection) == 1

        by_name_selection = controller.by_name("Light1")
        assert len(by_name_selection) == 1

    def test_duplicate_names(self):
        mock_lights = [MockLight("Flag"), MockLight("Flag"), MockLight("Unique")]
        mock_light_class = Mock()
        mock_light_class.all_lights.return_value = mock_lights

        controller = LightController(mock_light_class)

        # Get all with same name
        flags = controller.by_name("Flag")
        assert len(flags) == 2

        # Get specific by index
        flag1 = controller.by_name("Flag", index=0)
        assert len(flag1) == 1

        flag2 = controller.by_name("Flag", index=1)
        assert len(flag2) == 1

        # Check display names
        names = controller.names()
        assert "Flag #1" in names
        assert "Flag #2" in names
        assert "Unique" in names

    def test_context_manager(self):
        controller = LightController()

        with controller as ctx:
            assert ctx is controller

    def test_cleanup_and_release(self):
        mock_lights = [MockLight("Test")]
        mock_light_class = Mock()
        mock_light_class.all_lights.return_value = mock_lights

        controller = LightController(mock_light_class)

        # Access lights to populate
        _ = controller.lights

        controller.cleanup()
        controller.release_lights()


class TestLedFunctionality:
    """Test LED-specific functionality in the controller and selection classes."""

    def test_light_selection_turn_on_with_led_parameter(self):
        """Test that turn_on passes LED parameter to individual lights."""
        mock_light1 = MockLight("Light1")
        mock_light2 = MockLight("Light2")

        selection = LightSelection([mock_light1, mock_light2])

        # Test default LED (all LEDs)
        selection.turn_on((255, 0, 0))
        assert mock_light1.current_color == (255, 0, 0)
        assert mock_light1.current_led == 0
        assert mock_light2.current_color == (255, 0, 0)
        assert mock_light2.current_led == 0

        # Test specific LED
        selection.turn_on((0, 255, 0), led=1)
        assert mock_light1.current_color == (0, 255, 0)
        assert mock_light1.current_led == 1
        assert mock_light2.current_color == (0, 255, 0)
        assert mock_light2.current_led == 1

    def test_light_selection_blink_with_led_parameter(self):
        """Test that blink method accepts LED parameter."""
        mock_light = MockLight("TestLight")
        mock_light.add_task.return_value = Mock()

        selection = LightSelection([mock_light])

        # Test blink with LED parameter
        with patch("asyncio.get_running_loop", side_effect=RuntimeError):
            with patch("asyncio.run") as mock_run:
                selection.blink((255, 0, 0), count=3, led=2)
                mock_run.assert_called_once()

    def test_controller_fluent_interface_with_leds(self):
        """Test that controller methods work with LED parameters."""
        mock_lights = [MockLight("Blink1"), MockLight("Luxafor")]
        mock_light_class = Mock()
        mock_light_class.all_lights.return_value = mock_lights

        controller = LightController(mock_light_class)

        # Test turn_on with LED parameter via fluent interface
        controller.all().turn_on((0, 0, 255), led=1)

        for light in mock_lights:
            assert light.current_color == (0, 0, 255)
            assert light.current_led == 1

    def test_led_parameter_validation(self):
        """Test that LED parameter handles edge cases correctly."""
        mock_light = MockLight("TestLight")
        selection = LightSelection([mock_light])

        # Test negative LED (should still work, device will handle)
        selection.turn_on((255, 255, 255), led=-1)
        assert mock_light.current_led == -1

        # Test large LED number (should still work, device will handle)
        selection.turn_on((128, 128, 128), led=999)
        assert mock_light.current_led == 999

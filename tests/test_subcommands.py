"""Tests for CLI subcommands."""

from unittest.mock import Mock, patch

import pytest
import typer
from busylight.subcommands.blink import blink_cli
from busylight.subcommands.display import (
    display_cli,
    list_lights,
    list_supported_lights,
)
from busylight.subcommands.fli import fli_cli
from busylight.subcommands.off import deactivate_lights, off_cli
from busylight.subcommands.on import activate_lights, on_cli
from busylight.subcommands.pulse import pulse_cli
from busylight.subcommands.rainbow import rainbow_cli
from busylight.subcommands.udev_rules import udev_rules_cli


class TestDisplaySubcommand:
    """Test display CLI subcommands."""

    def test_display_cli_is_typer_instance(self):
        """display_cli should be a Typer instance."""
        assert isinstance(display_cli, typer.Typer)

    @patch("busylight.subcommands.display.get_light_selection")
    @patch("busylight.subcommands.display.typer")
    def test_list_lights_success(self, mock_typer, mock_get_selection):
        """Should list lights successfully."""
        mock_ctx = Mock()
        mock_light1 = Mock()
        mock_light1.name = "Light 1"
        mock_light2 = Mock()
        mock_light2.name = "Light 2"
        mock_selection = Mock()
        mock_selection.lights = [mock_light1, mock_light2]
        mock_get_selection.return_value = mock_selection

        list_lights(mock_ctx, verbose=False)

        mock_get_selection.assert_called_once_with(mock_ctx)

        mock_typer.secho.assert_called()

    @patch("busylight.subcommands.display.get_light_selection")
    def test_list_lights_no_lights_found(self, mock_get_selection):
        """Should handle NoLightsFoundError."""
        from busylight_core import Light, NoLightsFoundError

        mock_ctx = Mock()
        mock_get_selection.side_effect = NoLightsFoundError(Light)

        with patch("busylight.subcommands.display.typer.secho") as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                list_lights(mock_ctx, verbose=False)

        assert exc_info.value.exit_code == 1
        mock_secho.assert_called_with("No lights detected.", fg="red")

    @patch("busylight.subcommands.display.get_light_selection")
    @patch("busylight.subcommands.display.typer")
    def test_list_lights_verbose_mode(self, mock_typer, mock_get_selection):
        """Should show detailed info in verbose mode."""
        mock_ctx = Mock()
        mock_light = Mock()
        mock_light.name = "Test Light"
        mock_light.hardware.__dict__ = {"vid": 1234, "pid": 5678, "handle": "ignore"}
        mock_selection = Mock()
        mock_selection.lights = [mock_light]
        mock_get_selection.return_value = mock_selection

        list_lights(mock_ctx, verbose=True)

        assert mock_typer.secho.call_count > 2

    @patch("busylight.subcommands.display.Light")
    @patch("busylight.subcommands.display.typer")
    def test_list_supported_lights_non_verbose(self, mock_typer, mock_light):
        """Should list supported lights without verbose."""
        mock_light.supported_lights.return_value = {
            "Vendor1": ["Device1", "Device2"],
            "Vendor2": ["Device3"],
        }
        mock_typer.Exit = typer.Exit

        with pytest.raises(typer.Exit):
            list_supported_lights(verbose=False)

        mock_typer.secho.assert_called()

    @patch("busylight.subcommands.display.Light")
    @patch("busylight.subcommands.display.typer")
    def test_list_supported_lights_verbose(self, mock_typer, mock_light):
        """Should list supported lights with detailed info in verbose mode."""
        mock_subclass = Mock()
        mock_subclass.vendor.return_value = "TestVendor"
        mock_subclass.supported_device_ids = {(0x1234, 0x5678): "Test Device"}
        mock_light.subclasses.return_value = [mock_subclass]

        list_supported_lights(verbose=True)

        mock_typer.secho.assert_called()


class TestOnSubcommand:
    """Test on CLI subcommand."""

    def test_on_cli_is_typer_instance(self):
        """on_cli should be a Typer instance."""
        assert isinstance(on_cli, typer.Typer)

    @patch("busylight.subcommands.on.get_light_selection")
    def test_activate_lights_success(self, mock_get_selection):
        """Should activate lights successfully."""
        mock_ctx = Mock()
        mock_selection = Mock()
        mock_light = Mock()
        mock_light.__class__.__module__ = "regular_light"
        mock_light.tasks = {}
        mock_selection.lights = [mock_light]
        mock_get_selection.return_value = mock_selection

        activate_lights(mock_ctx, color=(255, 0, 0), led=0)

        mock_selection.turn_on.assert_called_once_with((255, 0, 0), led=0)

    @patch("busylight.subcommands.on.get_light_selection")
    @patch("busylight.subcommands.on.typer")
    def test_activate_lights_no_lights_found(self, mock_typer, mock_get_selection):
        """Should handle NoLightsFoundError."""
        from busylight_core import Light, NoLightsFoundError

        mock_ctx = Mock()
        mock_get_selection.side_effect = NoLightsFoundError(Light)
        mock_typer.Exit = typer.Exit

        with pytest.raises(typer.Exit) as exc_info:
            activate_lights(mock_ctx, color=(255, 0, 0))

        assert exc_info.value.exit_code == 1
        mock_typer.secho.assert_called_with("No lights found.", fg="red")

    @patch("busylight.subcommands.on.get_light_selection")
    @patch("busylight.subcommands.on.typer")
    def test_activate_lights_keyboard_interrupt(self, mock_typer, mock_get_selection):
        """Should handle KeyboardInterrupt gracefully."""
        mock_ctx = Mock()
        mock_selection = Mock()
        mock_light = Mock()
        mock_light.__class__.__module__ = "regular_light"
        mock_light.tasks = {}
        mock_selection.lights = [mock_light]
        mock_selection.turn_on.side_effect = KeyboardInterrupt()
        mock_get_selection.return_value = mock_selection

        activate_lights(mock_ctx, color=(255, 0, 0))

        mock_selection.turn_off.assert_called_once()

    @patch("busylight.subcommands.on.get_light_selection")
    @patch("busylight.subcommands.on.typer")
    def test_activate_lights_timeout_error(self, mock_typer, mock_get_selection):
        """Should handle TimeoutError gracefully."""
        mock_ctx = Mock()
        mock_selection = Mock()
        mock_light = Mock()
        mock_light.__class__.__module__ = "regular_light"
        mock_light.tasks = {}
        mock_selection.lights = [mock_light]
        mock_selection.turn_on.side_effect = TimeoutError()
        mock_get_selection.return_value = mock_selection

        activate_lights(mock_ctx, color=(255, 0, 0))

        mock_selection.turn_off.assert_called_once()

    @patch("busylight.subcommands.on.get_light_selection")
    @patch("busylight.subcommands.on.typer")
    def test_activate_lights_generic_exception(self, mock_typer, mock_get_selection):
        """Should handle generic exceptions."""
        mock_ctx = Mock()
        mock_selection = Mock()
        mock_light = Mock()
        mock_light.__class__.__module__ = "regular_light"
        mock_light.tasks = {}
        mock_selection.lights = [mock_light]
        mock_selection.turn_on.side_effect = Exception("Test error")
        mock_get_selection.return_value = mock_selection
        mock_typer.Exit = typer.Exit

        with pytest.raises(typer.Exit) as exc_info:
            activate_lights(mock_ctx, color=(255, 0, 0))

        assert exc_info.value.exit_code == 1
        mock_typer.secho.assert_called_with(
            "Error activating lights: Test error", fg="red"
        )


class TestOffSubcommand:
    """Test off CLI subcommand."""

    def test_off_cli_is_typer_instance(self):
        """off_cli should be a Typer instance."""
        assert isinstance(off_cli, typer.Typer)

    @patch("busylight.subcommands.off.get_light_selection")
    def test_deactivate_lights_success(self, mock_get_selection):
        """Should deactivate lights successfully."""
        mock_ctx = Mock()
        mock_selection = Mock()
        mock_get_selection.return_value = mock_selection

        deactivate_lights(mock_ctx)

        mock_selection.turn_off.assert_called_once()

    @patch("busylight.subcommands.off.get_light_selection")
    @patch("busylight.subcommands.off.typer")
    def test_deactivate_lights_no_lights_found(self, mock_typer, mock_get_selection):
        """Should handle NoLightsFoundError gracefully."""
        from busylight_core import Light, NoLightsFoundError

        mock_ctx = Mock()
        mock_get_selection.side_effect = NoLightsFoundError(Light)

        deactivate_lights(mock_ctx)

        mock_typer.secho.assert_called_with("No lights to turn off.", fg="red")


class TestBlinkSubcommand:
    """Test blink CLI subcommand."""

    def test_blink_cli_is_typer_instance(self):
        """blink_cli should be a Typer instance."""
        assert isinstance(blink_cli, typer.Typer)

    @patch("busylight.subcommands.blink.get_light_selection")
    def test_blink_lights_success(self, mock_get_selection):
        """Should apply blink effect successfully."""
        from busylight.speed import Speed
        from busylight.subcommands.blink import blink_lights

        mock_ctx = Mock()
        mock_selection = Mock()
        mock_get_selection.return_value = mock_selection

        blink_lights(mock_ctx, color=(255, 0, 0), speed=Speed.Fast, count=5, led=0)

        mock_selection.blink.assert_called_once_with((255, 0, 0), count=5, speed="fast", led=0)

    @patch("busylight.subcommands.blink.get_light_selection")
    def test_blink_lights_keyboard_interrupt(self, mock_get_selection):
        """Should handle KeyboardInterrupt gracefully."""
        from busylight.speed import Speed
        from busylight.subcommands.blink import blink_lights

        mock_ctx = Mock()
        mock_selection = Mock()
        mock_selection.blink.side_effect = KeyboardInterrupt()
        mock_get_selection.return_value = mock_selection

        blink_lights(mock_ctx, color=(255, 0, 0), speed=Speed.Slow, count=0)

        mock_selection.turn_off.assert_called_once()

    @patch("busylight.subcommands.blink.get_light_selection")
    def test_blink_lights_no_lights_found(self, mock_get_selection):
        """Should handle NoLightsFoundError."""
        from busylight.speed import Speed
        from busylight.subcommands.blink import blink_lights
        from busylight_core import Light, NoLightsFoundError

        mock_ctx = Mock()
        mock_get_selection.side_effect = NoLightsFoundError(Light)

        with patch("busylight.subcommands.blink.typer.secho") as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                blink_lights(mock_ctx, color=(255, 0, 0), speed=Speed.Medium, count=3)

        assert exc_info.value.exit_code == 1
        mock_secho.assert_called_with("Unable to blink lights.", fg="red")

    @patch("busylight.subcommands.blink.get_light_selection")
    def test_blink_lights_generic_exception(self, mock_get_selection):
        """Should handle generic exceptions."""
        from busylight.speed import Speed
        from busylight.subcommands.blink import blink_lights

        mock_ctx = Mock()
        mock_selection = Mock()
        mock_selection.blink.side_effect = Exception("Test error")
        mock_get_selection.return_value = mock_selection

        with patch("busylight.subcommands.blink.typer.secho") as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                blink_lights(mock_ctx, color=(255, 0, 0), speed=Speed.Fast, count=1)

        assert exc_info.value.exit_code == 1
        mock_secho.assert_called_with("Error blinking lights: Test error", fg="red")


class TestPulseSubcommand:
    """Test pulse CLI subcommand."""

    def test_pulse_cli_is_typer_instance(self):
        """pulse_cli should be a Typer instance."""
        assert isinstance(pulse_cli, typer.Typer)

    @patch("busylight.subcommands.pulse.get_light_selection")
    @patch("busylight.subcommands.pulse.Effects")
    def test_pulse_lights_success(self, mock_effects, mock_get_selection):
        """Should apply pulse effect successfully."""
        from busylight.speed import Speed
        from busylight.subcommands.pulse import pulse_lights

        mock_effect_instance = Mock()
        mock_effects.for_name.return_value = Mock(return_value=mock_effect_instance)
        mock_ctx = Mock()
        mock_ctx.obj.timeout = 30.0
        mock_selection = Mock()
        mock_get_selection.return_value = mock_selection

        pulse_lights(mock_ctx, color=(0, 255, 0), speed=Speed.Medium, count=3, led=0)

        mock_effects.for_name.assert_called_once_with("gradient")
        mock_effects.for_name.return_value.assert_called_once_with(
            (0, 255, 0), step=8, count=3
        )

        mock_selection.apply_effect.assert_called_once_with(
            mock_effect_instance, duration=30.0, interval=Speed.Medium.duty_cycle / 16, led=0
        )

    @patch("busylight.subcommands.pulse.get_light_selection")
    @patch("busylight.subcommands.pulse.Effects")
    def test_pulse_lights_timeout_error(self, mock_effects, mock_get_selection):
        """Should handle TimeoutError gracefully."""
        from busylight.speed import Speed
        from busylight.subcommands.pulse import pulse_lights

        mock_effect_instance = Mock()
        mock_effects.for_name.return_value = Mock(return_value=mock_effect_instance)
        mock_ctx = Mock()
        mock_ctx.obj.timeout = None
        mock_selection = Mock()
        mock_selection.apply_effect.side_effect = TimeoutError()
        mock_get_selection.return_value = mock_selection

        pulse_lights(mock_ctx, color=(0, 0, 255), speed=Speed.Fast, count=0, led=0)

        mock_selection.turn_off.assert_called_once()

    @patch("busylight.subcommands.pulse.get_light_selection")
    def test_pulse_lights_no_lights_found(self, mock_get_selection):
        """Should handle NoLightsFoundError."""
        from busylight.speed import Speed
        from busylight.subcommands.pulse import pulse_lights
        from busylight_core import Light, NoLightsFoundError

        mock_ctx = Mock()
        mock_get_selection.side_effect = NoLightsFoundError(Light)

        with patch("busylight.subcommands.pulse.typer.secho") as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                pulse_lights(mock_ctx, color=(128, 128, 128), speed=Speed.Slow, count=2, led=0)

        assert exc_info.value.exit_code == 1
        mock_secho.assert_called_with("Unable to pulse lights.", fg="red")

    @patch("busylight.subcommands.pulse.get_light_selection")
    @patch("busylight.subcommands.pulse.Effects")
    def test_pulse_lights_generic_exception(self, mock_effects, mock_get_selection):
        """Should handle generic exceptions."""
        from busylight.speed import Speed
        from busylight.subcommands.pulse import pulse_lights

        mock_effects.for_name.return_value = Mock(return_value=Mock())
        mock_ctx = Mock()
        mock_ctx.obj.timeout = None
        mock_selection = Mock()
        mock_selection.apply_effect.side_effect = Exception("Pulse test error")
        mock_get_selection.return_value = mock_selection

        with patch("busylight.subcommands.pulse.typer.secho") as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                pulse_lights(mock_ctx, color=(64, 64, 64), speed=Speed.Medium, count=1, led=0)

        assert exc_info.value.exit_code == 1
        mock_secho.assert_called_with("Error pulse lights: Pulse test error", fg="red")


class TestSubcommandCLIInstances:
    """Test that remaining subcommand CLI instances are Typer instances."""

    def test_rainbow_cli_is_typer_instance(self):
        """rainbow_cli should be a Typer instance."""
        assert isinstance(rainbow_cli, typer.Typer)

    def test_fli_cli_is_typer_instance(self):
        """fli_cli should be a Typer instance."""
        assert isinstance(fli_cli, typer.Typer)

    def test_udev_rules_cli_is_typer_instance(self):
        """udev_rules_cli should be a Typer instance."""
        assert isinstance(udev_rules_cli, typer.Typer)

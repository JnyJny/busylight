"""Tests for CLI subcommands."""

import pytest
from unittest.mock import Mock, patch
import typer

from busylight.subcommands.display import display_cli, list_lights, list_supported_lights
from busylight.subcommands.on import on_cli, activate_lights  
from busylight.subcommands.off import off_cli, deactivate_lights
from busylight.subcommands.blink import blink_cli
from busylight.subcommands.pulse import pulse_cli
from busylight.subcommands.rainbow import rainbow_cli
from busylight.subcommands.fli import fli_cli
from busylight.subcommands.udev_rules import udev_rules_cli


class TestDisplaySubcommand:
    """Test display CLI subcommands."""
    
    def test_display_cli_is_typer_instance(self):
        """display_cli should be a Typer instance."""
        assert isinstance(display_cli, typer.Typer)
    
    @patch('busylight.subcommands.display.typer')  
    def test_list_lights_success(self, mock_typer):
        """Should list lights successfully."""
        # Create mock context and lights
        mock_ctx = Mock()
        mock_light1 = Mock()
        mock_light1.name = "Light 1" 
        mock_light2 = Mock()
        mock_light2.name = "Light 2"
        mock_ctx.obj.manager.selected_lights.return_value = [mock_light1, mock_light2]
        mock_ctx.obj.lights = []
        
        list_lights(mock_ctx, verbose=False)
        
        # Should call selected_lights
        mock_ctx.obj.manager.selected_lights.assert_called_once_with([])
        
        # Should print light names
        mock_typer.secho.assert_called()
    
    def test_list_lights_no_lights_found(self):
        """Should handle NoLightsFoundError."""
        from busylight_core import NoLightsFoundError, Light
        mock_ctx = Mock()
        mock_ctx.obj.manager.selected_lights.side_effect = NoLightsFoundError(Light)
        
        with patch('busylight.subcommands.display.typer.secho') as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                list_lights(mock_ctx, verbose=False)
                
        assert exc_info.value.exit_code == 1
        mock_secho.assert_called_with("No lights detected.", fg="red")
    
    @patch('busylight.subcommands.display.typer')
    def test_list_lights_verbose_mode(self, mock_typer):
        """Should show detailed info in verbose mode."""
        mock_ctx = Mock()
        mock_light = Mock()
        mock_light.name = "Test Light"
        mock_light.hardware.__dict__ = {"vid": 1234, "pid": 5678, "handle": "ignore"}
        mock_ctx.obj.manager.selected_lights.return_value = [mock_light]
        mock_ctx.obj.lights = []
        
        list_lights(mock_ctx, verbose=True)
        
        # Should print hardware details (multiple calls to secho)
        assert mock_typer.secho.call_count > 2
    
    @patch('busylight.subcommands.display.Light')
    @patch('busylight.subcommands.display.typer')
    def test_list_supported_lights_non_verbose(self, mock_typer, mock_light):
        """Should list supported lights without verbose."""
        mock_light.supported_lights.return_value = {
            "Vendor1": ["Device1", "Device2"],
            "Vendor2": ["Device3"]
        }
        mock_typer.Exit = typer.Exit
        
        with pytest.raises(typer.Exit):
            list_supported_lights(verbose=False)
            
        # Should print vendor names and device names
        mock_typer.secho.assert_called()
    
    @patch('busylight.subcommands.display.Light')  
    @patch('busylight.subcommands.display.typer')
    def test_list_supported_lights_verbose(self, mock_typer, mock_light):
        """Should list supported lights with detailed info in verbose mode."""
        mock_subclass = Mock()
        mock_subclass.vendor.return_value = "TestVendor"
        mock_subclass.supported_device_ids = {(0x1234, 0x5678): "Test Device"}
        mock_light.subclasses.return_value = [mock_subclass]
        
        list_supported_lights(verbose=True)
        
        # Should print device IDs and names
        mock_typer.secho.assert_called()


class TestOnSubcommand:
    """Test on CLI subcommand."""
    
    def test_on_cli_is_typer_instance(self):
        """on_cli should be a Typer instance."""
        assert isinstance(on_cli, typer.Typer)
    
    def test_activate_lights_success(self):
        """Should activate lights successfully."""
        mock_ctx = Mock()
        
        activate_lights(mock_ctx, color=(255, 0, 0))
        
        # Should call manager.on with color
        mock_ctx.obj.manager.on.assert_called_once_with(
            (255, 0, 0), mock_ctx.obj.lights, timeout=mock_ctx.obj.timeout
        )
    
    @patch('busylight.subcommands.on.typer')
    def test_activate_lights_no_lights_found(self, mock_typer):
        """Should handle NoLightsFoundError."""
        from busylight_core import NoLightsFoundError, Light
        mock_ctx = Mock()
        mock_ctx.obj.manager.on.side_effect = NoLightsFoundError(Light)
        mock_typer.Exit = typer.Exit
        
        with pytest.raises(typer.Exit) as exc_info:
            activate_lights(mock_ctx, color=(255, 0, 0))
            
        assert exc_info.value.exit_code == 1
        mock_typer.secho.assert_called_with("No lights found.", fg="red")
    
    @patch('busylight.subcommands.on.typer')
    def test_activate_lights_keyboard_interrupt(self, mock_typer):
        """Should handle KeyboardInterrupt gracefully."""
        mock_ctx = Mock()
        mock_ctx.obj.manager.on.side_effect = KeyboardInterrupt()
        
        activate_lights(mock_ctx, color=(255, 0, 0))
        
        # Should call manager.off to turn off lights
        mock_ctx.obj.manager.off.assert_called_once_with(mock_ctx.obj.lights)
    
    @patch('busylight.subcommands.on.typer')
    def test_activate_lights_timeout_error(self, mock_typer):
        """Should handle TimeoutError gracefully."""
        mock_ctx = Mock()
        mock_ctx.obj.manager.on.side_effect = TimeoutError()
        
        activate_lights(mock_ctx, color=(255, 0, 0))
        
        # Should call manager.off to turn off lights
        mock_ctx.obj.manager.off.assert_called_once_with(mock_ctx.obj.lights)
    
    @patch('busylight.subcommands.on.typer')
    def test_activate_lights_generic_exception(self, mock_typer):
        """Should handle generic exceptions."""
        mock_ctx = Mock()
        mock_ctx.obj.manager.on.side_effect = Exception("Test error")
        mock_typer.Exit = typer.Exit
        
        with pytest.raises(typer.Exit) as exc_info:
            activate_lights(mock_ctx, color=(255, 0, 0))
            
        assert exc_info.value.exit_code == 1
        mock_typer.secho.assert_called_with("Error activating lights: Test error", fg="red")


class TestOffSubcommand:
    """Test off CLI subcommand."""
    
    def test_off_cli_is_typer_instance(self):
        """off_cli should be a Typer instance."""
        assert isinstance(off_cli, typer.Typer)
    
    def test_deactivate_lights_success(self):
        """Should deactivate lights successfully."""
        mock_ctx = Mock()
        
        deactivate_lights(mock_ctx)
        
        # Should call manager.off
        mock_ctx.obj.manager.off.assert_called_once_with(mock_ctx.obj.lights)
    
    @patch('busylight.subcommands.off.typer')
    def test_deactivate_lights_no_lights_found(self, mock_typer):
        """Should handle NoLightsFoundError gracefully."""
        from busylight_core import NoLightsFoundError, Light
        mock_ctx = Mock()
        mock_ctx.obj.manager.off.side_effect = NoLightsFoundError(Light)
        
        # Should not raise exception, just print message
        deactivate_lights(mock_ctx)
        
        mock_typer.secho.assert_called_with("No lights to turn off.", fg="red")


class TestBlinkSubcommand:
    """Test blink CLI subcommand."""
    
    def test_blink_cli_is_typer_instance(self):
        """blink_cli should be a Typer instance."""
        assert isinstance(blink_cli, typer.Typer)
    
    @patch('busylight.subcommands.blink.Effects')
    def test_blink_lights_success(self, mock_effects):
        """Should apply blink effect successfully."""
        from busylight.subcommands.blink import blink_lights
        from busylight.speed import Speed
        
        mock_effect_instance = Mock()
        mock_effects.for_name.return_value = Mock(return_value=mock_effect_instance)
        mock_ctx = Mock()
        
        blink_lights(mock_ctx, color=(255, 0, 0), speed=Speed.Fast, count=5)
        
        # Should create blink effect
        mock_effects.for_name.assert_called_once_with("blink")
        mock_effects.for_name.return_value.assert_called_once_with((255, 0, 0), count=5)
        
        # Should apply effect
        mock_ctx.obj.manager.apply_effect.assert_called_once_with(
            mock_effect_instance,
            duty_cycle=Speed.Fast.duty_cycle,
            light_ids=mock_ctx.obj.lights,
            timeout=mock_ctx.obj.timeout
        )
    
    @patch('busylight.subcommands.blink.Effects')
    def test_blink_lights_keyboard_interrupt(self, mock_effects):
        """Should handle KeyboardInterrupt gracefully."""
        from busylight.subcommands.blink import blink_lights
        from busylight.speed import Speed
        
        mock_effect_instance = Mock()
        mock_effects.for_name.return_value = Mock(return_value=mock_effect_instance)
        mock_ctx = Mock()
        mock_ctx.obj.manager.apply_effect.side_effect = KeyboardInterrupt()
        
        blink_lights(mock_ctx, color=(255, 0, 0), speed=Speed.Slow, count=0)
        
        # Should turn off lights
        mock_ctx.obj.manager.off.assert_called_once_with(mock_ctx.obj.lights)
    
    @patch('busylight.subcommands.blink.Effects')
    def test_blink_lights_no_lights_found(self, mock_effects):
        """Should handle NoLightsFoundError."""
        from busylight.subcommands.blink import blink_lights
        from busylight.speed import Speed
        from busylight_core import NoLightsFoundError, Light
        
        mock_effects.for_name.return_value = Mock(return_value=Mock())
        mock_ctx = Mock()
        mock_ctx.obj.manager.apply_effect.side_effect = NoLightsFoundError(Light)
        
        with patch('busylight.subcommands.blink.typer.secho') as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                blink_lights(mock_ctx, color=(255, 0, 0), speed=Speed.Medium, count=3)
                
        assert exc_info.value.exit_code == 1
        mock_secho.assert_called_with("Unable to blink lights.", fg="red")
    
    @patch('busylight.subcommands.blink.Effects')
    def test_blink_lights_generic_exception(self, mock_effects):
        """Should handle generic exceptions."""
        from busylight.subcommands.blink import blink_lights
        from busylight.speed import Speed
        
        mock_effects.for_name.return_value = Mock(return_value=Mock())
        mock_ctx = Mock()
        mock_ctx.obj.manager.apply_effect.side_effect = Exception("Test error")
        
        with patch('busylight.subcommands.blink.typer.secho') as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                blink_lights(mock_ctx, color=(255, 0, 0), speed=Speed.Fast, count=1)
                
        assert exc_info.value.exit_code == 1
        mock_secho.assert_called_with("Error blinking lights: Test error", fg="red")


class TestPulseSubcommand:
    """Test pulse CLI subcommand."""
    
    def test_pulse_cli_is_typer_instance(self):
        """pulse_cli should be a Typer instance."""  
        assert isinstance(pulse_cli, typer.Typer)
    
    @patch('busylight.subcommands.pulse.Effects')
    def test_pulse_lights_success(self, mock_effects):
        """Should apply pulse effect successfully."""
        from busylight.subcommands.pulse import pulse_lights
        from busylight.speed import Speed
        
        mock_effect_instance = Mock()
        mock_effects.for_name.return_value = Mock(return_value=mock_effect_instance)
        mock_ctx = Mock()
        
        pulse_lights(mock_ctx, color=(0, 255, 0), speed=Speed.Medium, count=3)
        
        # Should create gradient effect for pulse
        mock_effects.for_name.assert_called_once_with("gradient")
        mock_effects.for_name.return_value.assert_called_once_with((0, 255, 0), step=8, count=3)
        
        # Should apply effect with modified duty cycle
        mock_ctx.obj.manager.apply_effect.assert_called_once_with(
            mock_effect_instance,
            duty_cycle=Speed.Medium.duty_cycle / 16,
            light_ids=mock_ctx.obj.lights,
            timeout=mock_ctx.obj.timeout
        )
    
    @patch('busylight.subcommands.pulse.Effects')
    def test_pulse_lights_timeout_error(self, mock_effects):
        """Should handle TimeoutError gracefully."""
        from busylight.subcommands.pulse import pulse_lights
        from busylight.speed import Speed
        
        mock_effect_instance = Mock()
        mock_effects.for_name.return_value = Mock(return_value=mock_effect_instance)
        mock_ctx = Mock()
        mock_ctx.obj.manager.apply_effect.side_effect = TimeoutError()
        
        pulse_lights(mock_ctx, color=(0, 0, 255), speed=Speed.Fast, count=0)
        
        # Should turn off lights
        mock_ctx.obj.manager.off.assert_called_once_with(mock_ctx.obj.lights)
    
    @patch('busylight.subcommands.pulse.Effects')
    def test_pulse_lights_no_lights_found(self, mock_effects):
        """Should handle NoLightsFoundError."""
        from busylight.subcommands.pulse import pulse_lights
        from busylight.speed import Speed
        from busylight_core import NoLightsFoundError, Light
        
        mock_effects.for_name.return_value = Mock(return_value=Mock())
        mock_ctx = Mock()
        mock_ctx.obj.manager.apply_effect.side_effect = NoLightsFoundError(Light)
        
        with patch('busylight.subcommands.pulse.typer.secho') as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                pulse_lights(mock_ctx, color=(128, 128, 128), speed=Speed.Slow, count=2)
                
        assert exc_info.value.exit_code == 1
        mock_secho.assert_called_with("Unable to pulse lights.", fg="red")
    
    @patch('busylight.subcommands.pulse.Effects')
    def test_pulse_lights_generic_exception(self, mock_effects):
        """Should handle generic exceptions."""
        from busylight.subcommands.pulse import pulse_lights
        from busylight.speed import Speed
        
        mock_effects.for_name.return_value = Mock(return_value=Mock())
        mock_ctx = Mock()
        mock_ctx.obj.manager.apply_effect.side_effect = Exception("Pulse test error")
        
        with patch('busylight.subcommands.pulse.typer.secho') as mock_secho:
            with pytest.raises(typer.Exit) as exc_info:
                pulse_lights(mock_ctx, color=(64, 64, 64), speed=Speed.Medium, count=1)
                
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
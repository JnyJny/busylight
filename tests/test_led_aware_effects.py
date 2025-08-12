"""Tests for LED-aware effects functionality."""

import asyncio
import inspect
from unittest.mock import Mock

from busylight.effects import Blink, Steady, Spectrum, Gradient


class TestLedAwareEffects:
    """Test LED targeting for all effects."""

    def test_base_effect_execute_signature(self):
        """Test that BaseEffect.execute() accepts LED parameter."""
        effect = Blink((255, 0, 0))
        
        # Test that execute accepts led parameter without error
        signature = inspect.signature(effect.execute)
        assert 'led' in signature.parameters
        assert signature.parameters['led'].default == 0

    def test_steady_effect_led_parameter(self):
        """Test Steady effect with LED parameter."""
        effect = Steady((255, 0, 0))
        mock_light = Mock()
        
        # Run the effect with LED parameter
        asyncio.run(effect.execute(mock_light, led=1))
        
        # Verify light.on was called with LED parameter
        mock_light.on.assert_called_once_with((255, 0, 0), led=1)

    def test_blink_effect_led_parameter(self):
        """Test Blink effect with LED parameter."""
        effect = Blink((255, 0, 0), count=2)
        mock_light = Mock()
        
        # Mock the async execution
        async def run_effect():
            await effect.execute(mock_light, interval=0.01, led=2)
        
        asyncio.run(run_effect())
        
        # Verify light.on calls included LED parameter
        assert mock_light.on.call_count >= 2
        for call in mock_light.on.call_args_list:
            assert call.kwargs.get('led') == 2

    def test_spectrum_effect_led_parameter(self):
        """Test Spectrum effect with LED parameter."""
        effect = Spectrum(steps=3, count=1)  # Small steps for quick test
        mock_light = Mock()
        
        async def run_effect():
            await effect.execute(mock_light, interval=0.01, led=1)
        
        asyncio.run(run_effect())
        
        # Verify light.on calls included LED parameter
        assert mock_light.on.call_count >= 3
        for call in mock_light.on.call_args_list:
            assert call.kwargs.get('led') == 1

    def test_gradient_effect_led_parameter(self):
        """Test Gradient effect with LED parameter."""
        effect = Gradient((255, 0, 0), step=50, step_max=100, count=1)  # Small steps
        mock_light = Mock()
        
        async def run_effect():
            await effect.execute(mock_light, interval=0.01, led=2)
        
        asyncio.run(run_effect())
        
        # Verify light.on calls included LED parameter
        assert mock_light.on.call_count >= 2
        for call in mock_light.on.call_args_list:
            assert call.kwargs.get('led') == 2


class TestCliLedSupport:
    """Test CLI LED support."""

    def test_rainbow_cli_has_led_parameter(self):
        """Test rainbow CLI command accepts LED parameter."""
        from busylight.subcommands.rainbow import rainbow_lights
        
        signature = inspect.signature(rainbow_lights)
        assert 'led' in signature.parameters

    def test_pulse_cli_has_led_parameter(self):
        """Test pulse CLI command accepts LED parameter."""
        from busylight.subcommands.pulse import pulse_lights
        
        signature = inspect.signature(pulse_lights)
        assert 'led' in signature.parameters

    def test_fli_cli_has_led_parameter(self):
        """Test fli CLI command accepts LED parameter."""
        from busylight.subcommands.fli import flash_lights_impressively
        
        signature = inspect.signature(flash_lights_impressively)
        assert 'led' in signature.parameters

    def test_blink_cli_has_led_parameter(self):
        """Test blink CLI command accepts LED parameter."""
        from busylight.subcommands.blink import blink_lights
        
        signature = inspect.signature(blink_lights)
        assert 'led' in signature.parameters


class TestBackwardCompatibility:
    """Test backward compatibility of LED-aware effects."""

    def test_effects_work_without_led_parameter(self):
        """Test that effects still work without LED parameter."""
        effect = Steady((255, 0, 0))
        mock_light = Mock()
        
        # Should work without LED parameter (defaults to led=0)
        asyncio.run(effect.execute(mock_light))
        
        # Verify light.on was called with default LED parameter
        mock_light.on.assert_called_once_with((255, 0, 0), led=0)

    def test_apply_effect_signature_includes_led(self):
        """Test that apply_effect method includes LED parameter."""
        from busylight.controller import LightSelection
        
        # Check method signature
        signature = inspect.signature(LightSelection.apply_effect)
        assert 'led' in signature.parameters
        assert signature.parameters['led'].default == 0

    def test_blink_method_signature_includes_led(self):
        """Test that blink method includes LED parameter.""" 
        from busylight.controller import LightSelection
        
        # Check method signature
        signature = inspect.signature(LightSelection.blink)
        assert 'led' in signature.parameters
        assert signature.parameters['led'].default == 0


class TestEffectIntegration:
    """Test effect integration with LED parameters."""

    def test_all_effects_have_led_aware_execute(self):
        """Test that all built-in effects support LED parameter."""
        from busylight.effects import Blink, Steady, Spectrum, Gradient
        
        effects = [
            Blink((255, 0, 0)),
            Steady((0, 255, 0)), 
            Spectrum(steps=5),
            Gradient((0, 0, 255), step=10, step_max=50)
        ]
        
        for effect in effects:
            signature = inspect.signature(effect.execute)
            assert 'led' in signature.parameters
            assert signature.parameters['led'].default == 0

    def test_led_parameter_propagation(self):
        """Test LED parameter propagates through effect execution."""
        effect = Steady((255, 0, 0))
        mock_light = Mock()
        
        # Test various LED values
        for led_value in [0, 1, 2, 3]:
            mock_light.reset_mock()
            asyncio.run(effect.execute(mock_light, led=led_value))
            mock_light.on.assert_called_once_with((255, 0, 0), led=led_value)
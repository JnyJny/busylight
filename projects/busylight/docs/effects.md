# Effects System

The BusyLight Effects system provides a powerful framework for creating
dynamic lighting patterns. This guide covers the built-in effects and
how to create custom effects.

## Built-in Effects

### Steady

Static color display - the simplest effect.

**Parameters:**
- `color`: RGB tuple for the target color

**Usage:**
```python
from busylight.effects import Steady

# Create steady red effect
effect = Steady(color=(255, 0, 0))
```

**CLI Examples:**
```bash
# All LEDs
busylight on red

# Target specific LED (for multi-LED devices)
busylight on red --led 1    # First/top LED only
busylight on blue --led 2   # Second/bottom LED only
```

### Blink

Alternates between two colors with configurable timing.

**Parameters:**
- `on_color`: RGB tuple for the "on" state
- `off_color`: RGB tuple for the "off" state (defaults to black)
- `count`: Number of blink cycles (0 = infinite)

**Usage:**
```python
from busylight.effects import Blink

# Blink red/black 5 times
effect = Blink(
    on_color=(255, 0, 0),
    off_color=(0, 0, 0),
    count=5
)
```

**CLI Examples:**
```bash
# Blink all LEDs
busylight blink red --count 5

# Target specific LED for blinking
busylight blink yellow --led 1 --count 3   # Top LED only
busylight blink blue --led 2               # Bottom LED infinite
```

### Spectrum (Rainbow)

Generates smooth color transitions through the full spectrum.

**Parameters:**
- `scale`: Color intensity (0.0 to 1.0)
- `steps`: Number of colors in spectrum (default: 64)
- `frequency`: RGB frequency tuple for sine wave generation
- `phase`: RGB phase offset tuple
- `center`: Center value for sine wave (default: 128)
- `width`: Amplitude of sine wave (default: 127)
- `count`: Number of spectrum cycles (0 = infinite)

**Usage:**
```python
from busylight.effects import Spectrum

# Create rainbow effect
effect = Spectrum(scale=0.8, steps=32, count=3)
```

**CLI Examples:**
```bash
# Rainbow on all LEDs
busylight rainbow --count 3

# Target specific LED for rainbow effect
busylight rainbow --led 1 --speed fast     # Top LED only
busylight rainbow --led 2 --count 1        # Bottom LED, one cycle
```

### Gradient

Smooth transition from black to a target color and back.

**Parameters:**
- `color`: Target RGB color for the gradient
- `step`: Step size for gradient calculation (default: 1)
- `step_max`: Maximum step value, controls smoothness (default: 255)
- `count`: Number of gradient cycles (0 = infinite)

**Usage:**
```python
from busylight.effects import Gradient

# Pulsing blue effect
effect = Gradient(
    color=(0, 0, 255),
    step=5,
    count=2
)
```

**CLI Examples:**
```bash
# Pulse all LEDs
busylight pulse blue --count 2

# Target specific LED for pulsing
busylight pulse green --led 1 --speed slow   # Top LED only
busylight pulse red --led 2 --count 5        # Bottom LED, 5 pulses
```

## LED Targeting for Multi-LED Devices

BusyLight supports devices with multiple LEDs (like Blink1 mk2) through LED targeting. All effects can be applied to specific LEDs using the `--led` parameter.

### LED Index Convention

- **`0`**: All LEDs (default behavior)
- **`1`**: First/top LED
- **`2`**: Second/bottom LED  
- **`3+`**: Additional LEDs (device-dependent)

### Multi-LED Effect Examples

#### Split LED Effects
```bash
# Different colors on different LEDs
busylight on red --led 1      # Top LED red
busylight on blue --led 2     # Bottom LED blue (simultaneously)

# Different effects on different LEDs
busylight blink green --led 1 --count 3    # Top LED blinks
busylight pulse orange --led 2             # Bottom LED pulses
```

#### Sequential LED Programming
```bash
# Program LEDs one by one
busylight on red --led 1 && sleep 1 && busylight on blue --led 2
busylight rainbow --led 1 & busylight pulse red --led 2
```

#### Web API LED Targeting
```bash
# All LEDs
curl "http://localhost:8000/lights/on?color=red"

# Specific LED
curl "http://localhost:8000/lights/on?color=blue&led=1"
curl "http://localhost:8000/light/0/rainbow?led=2&speed=fast"
curl "http://localhost:8000/lights/pulse?color=green&led=1&count=3"
```

### Python API LED Targeting

```python
from busylight.controller import LightController

with LightController() as controller:
    # All LEDs (default)
    controller.all().turn_on("red")
    
    # Specific LED targeting using apply_effect
    from busylight.effects import Blink, Spectrum, Gradient
    
    # LED-specific effects
    controller.all().apply_effect(Blink((255, 0, 0), count=5), led=1)
    controller.all().apply_effect(Spectrum(scale=0.8), led=2)
    controller.all().apply_effect(Gradient((0, 255, 0)), led=1)
    
    # LED-specific basic operations
    controller.all().turn_on((255, 0, 0), led=1)    # Top LED red
    controller.all().turn_on((0, 0, 255), led=2)    # Bottom LED blue
    controller.all().blink((255, 255, 0), led=1, count=3)  # Top LED blink yellow
```

### Device Compatibility

**Known Multi-LED Devices:**
- **Blink1 mk2**: 2 LEDs (top/bottom)
- **Luxafor Flag**: Multiple LEDs in sequence

**Single-LED Devices:** LED parameter is ignored safely
- **Blynclight Plus, MuteMe Original, fit-statUSB**: `--led` parameter has no effect

### Advanced LED Patterns

```python
# Create complex multi-LED effects
async def multi_led_pattern():
    controller = LightController()
    
    # Alternating pattern
    controller.all().apply_effect(Blink((255, 0, 0)), led=1)  # Top red blink
    await asyncio.sleep(0.5)
    controller.all().apply_effect(Blink((0, 255, 0)), led=2)  # Bottom green blink
    
    # Synchronized different effects
    tasks = [
        controller.all().apply_effect(Spectrum(), led=1),      # Top rainbow
        controller.all().apply_effect(Gradient((255, 0, 0)), led=2)  # Bottom pulse
    ]
    await asyncio.gather(*tasks)
```

## Effect Architecture

### Base Class: BaseEffect

All effects inherit from `BaseEffect`, which provides:

#### Core Properties

```python
@property
@abc.abstractmethod
def colors(self) -> list[tuple[int, int, int]]:
    """List of RGB color tuples that define the effect sequence."""

@property  
@abc.abstractmethod
def default_interval(self) -> float:
    """Default interval between color changes in seconds."""
```

#### Common Attributes

- **`name`**: Effect class name (auto-generated)
- **`count`**: Number of effect cycles (0 = infinite)
- **`priority`**: Task priority from `TaskPriority` enum

#### Discovery System

```python
# Get all available effects
effect_names = BaseEffect.effects()
# ['steady', 'blink', 'spectrum', 'gradient']

# Create effect by name
effect_class = BaseEffect.for_name("blink")
effect = effect_class(on_color=(255, 0, 0))
```

#### Execution Model

Effects run asynchronously using the `execute()` method:

```python
async def execute(self, light: "Light", interval: float | None = None) -> None:
    """Execute this effect on the given light.
    
    :param light: Light instance with TaskableMixin capabilities
    :param interval: Override default interval between color changes
    """
```

The base implementation handles:
- Color cycling with proper count handling
- Interval timing between color changes
- LED targeting for multi-LED devices
- Automatic cleanup (turning off light when done)

## Creating Custom Effects

### Step 1: Define Your Effect Class

```python
from typing import TYPE_CHECKING
from busylight_core.mixins.taskable import TaskPriority
from busylight.effects.effect import BaseEffect

if TYPE_CHECKING:
    from busylight_core import Light

class CustomEffect(BaseEffect):
    def __init__(self, param1: str, param2: int = 0) -> None:
        """Initialize your custom effect.
        
        :param param1: Custom parameter description
        :param param2: Another parameter with default value
        """
        self.param1 = param1
        self.param2 = param2
        self.priority = TaskPriority.NORMAL
    
    @property
    def colors(self) -> list[tuple[int, int, int]]:
        """Generate your color sequence."""
        # Return list of RGB tuples
        return [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    
    @property
    def default_interval(self) -> float:
        """Return default timing between colors."""
        return 0.2  # 200ms between color changes
```

### Step 2: Advanced Color Generation

#### Static Color Sequences

```python
@property
def colors(self) -> list[tuple[int, int, int]]:
    """Simple predefined sequence."""
    return [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange  
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
    ]
```

#### Computed Color Sequences

```python
@property
def colors(self) -> list[tuple[int, int, int]]:
    """Generate colors algorithmically."""
    if hasattr(self, "_colors"):
        return self._colors
    
    colors = []
    for i in range(10):
        # Create fading red effect
        intensity = int(255 * (i / 10))
        colors.append((intensity, 0, 0))
    
    # Cache the computed colors
    self._colors = colors
    return self._colors
```

#### Parameterized Color Generation

```python
class ParameterizedEffect(BaseEffect):
    def __init__(self, base_color: tuple[int, int, int], steps: int = 10):
        self.base_color = base_color
        self.steps = steps
        self.priority = TaskPriority.LOW
    
    @property
    def colors(self) -> list[tuple[int, int, int]]:
        """Generate gradient based on parameters."""
        if hasattr(self, "_colors"):
            return self._colors
            
        r, g, b = self.base_color
        colors = []
        
        for i in range(self.steps):
            # Create brightness ramp
            scale = i / (self.steps - 1)
            colors.append((
                int(r * scale),
                int(g * scale), 
                int(b * scale)
            ))
        
        # Add reverse for smooth cycle
        self._colors = colors + list(reversed(colors[:-1]))
        return self._colors
    
    @property
    def default_interval(self) -> float:
        return 0.1
```

### Step 3: Custom Execution Logic

For advanced effects, override the `execute()` method:

```python
class CustomTimingEffect(BaseEffect):
    async def execute(self, light: "Light", interval: float | None = None, led: int = 0) -> None:
        """Custom execution with variable timing and LED support."""
        try:
            for i, color in enumerate(self.colors):
                light.on(color, led=led)  # Pass LED parameter
                
                # Variable timing based on position
                if i < len(self.colors) // 2:
                    await asyncio.sleep(0.1)  # Fast first half
                else:
                    await asyncio.sleep(0.5)  # Slow second half
                    
        finally:
            light.off(led=led)  # Clean up specific LED
```

### Step 4: Register Your Effect

Add to the effects module:

```python
# In src/busylight/effects/__init__.py
from .custom_effect import CustomEffect

__all__ = [
    "Blink",
    "CustomEffect",  # Add your effect
    "Effects", 
    "Gradient",
    "Spectrum",
    "Steady",
]
```

## Effect Guidelines

### Performance Considerations

1. **Cache Computed Colors**: Use `self._colors` to avoid recalculation
2. **Reasonable Color Counts**: Keep color sequences under 1000 items
3. **Appropriate Intervals**: Balance smoothness with device capabilities
4. **Priority Setting**: Use `TaskPriority.LOW` for resource-intensive effects

### Color Generation Best Practices

```python
# ✅ Good: Cached computation
@property
def colors(self) -> list[tuple[int, int, int]]:
    if hasattr(self, "_colors"):
        return self._colors
    
    # Expensive computation here
    self._colors = computed_colors
    return self._colors

# ❌ Bad: Recalculates every time
@property 
def colors(self) -> list[tuple[int, int, int]]:
    return [expensive_computation() for _ in range(100)]
```

### Timing Guidelines

- **Fast effects**: 0.01 - 0.1 seconds (animations, rapid blinks)
- **Medium effects**: 0.1 - 0.5 seconds (smooth transitions)
- **Slow effects**: 0.5 - 2.0 seconds (gentle pulses, ambient)

### Error Handling

```python
@property
def colors(self) -> list[tuple[int, int, int]]:
    try:
        return self._generate_colors()
    except Exception:
        # Fallback to simple sequence
        return [(255, 0, 0), (0, 0, 0)]  # Red blink
```

## Advanced Patterns

### Conditional Color Generation

```python
class AdaptiveEffect(BaseEffect):
    def __init__(self, intensity: str = "normal"):
        self.intensity = intensity
        self.priority = TaskPriority.NORMAL
    
    @property
    def colors(self) -> list[tuple[int, int, int]]:
        if self.intensity == "low":
            max_brightness = 64
        elif self.intensity == "high":
            max_brightness = 255
        else:
            max_brightness = 128
            
        return [(max_brightness, 0, 0), (0, 0, 0)]
```

### Mathematical Color Functions

```python
import math

class SineWaveEffect(BaseEffect):
    def __init__(self, frequency: float = 0.1, amplitude: int = 127):
        self.frequency = frequency
        self.amplitude = amplitude
        self.priority = TaskPriority.LOW
    
    @property
    def colors(self) -> list[tuple[int, int, int]]:
        colors = []
        for i in range(50):
            # Sine wave for smooth color transitions
            value = int(self.amplitude * math.sin(i * self.frequency) + 128)
            colors.append((value, 0, 128 - value))
        return colors
```

### Multi-Phase Effects

```python
class MultiPhaseEffect(BaseEffect):
    @property
    def colors(self) -> list[tuple[int, int, int]]:
        phase1 = [(255, 0, 0)] * 5      # Red phase
        phase2 = [(0, 255, 0)] * 3      # Green phase  
        phase3 = [(0, 0, 255)] * 7      # Blue phase
        return phase1 + phase2 + phase3
```

## Testing Custom Effects

### Unit Testing

```python
import pytest
from your_module import CustomEffect

def test_custom_effect_colors():
    effect = CustomEffect(param1="test")
    colors = effect.colors
    
    assert len(colors) > 0
    assert all(len(color) == 3 for color in colors)
    assert all(0 <= c <= 255 for color in colors for c in color)

def test_custom_effect_timing():
    effect = CustomEffect(param1="test")
    assert effect.default_interval > 0
```

### Integration Testing

```python
import asyncio
from unittest.mock import Mock

async def test_effect_execution():
    effect = CustomEffect(param1="test")
    mock_light = Mock()
    
    # Test execution doesn't raise errors
    await effect.execute(mock_light, interval=0.01)
    
    # Verify light was called
    assert mock_light.on.called
    assert mock_light.off.called
```

### CLI Testing

```bash
# Test via CLI (requires actual device)
busylight --effect custom_effect --param1 test
```

Custom effects provide unlimited creative possibilities for lighting patterns.
The key is understanding the color generation system and execution model
provided by the BaseEffect framework.
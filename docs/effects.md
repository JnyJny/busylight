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

**CLI Example:**
```bash
busylight on red
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

**CLI Example:**
```bash
busylight blink red --count 5
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

**CLI Example:**
```bash
busylight rainbow --count 3
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

**CLI Example:**
```bash
busylight pulse blue --count 2
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
    async def execute(self, light: "Light", interval: float | None = None) -> None:
        """Custom execution with variable timing."""
        try:
            for i, color in enumerate(self.colors):
                light.on(color)
                
                # Variable timing based on position
                if i < len(self.colors) // 2:
                    await asyncio.sleep(0.1)  # Fast first half
                else:
                    await asyncio.sleep(0.5)  # Slow second half
                    
        finally:
            light.off()
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
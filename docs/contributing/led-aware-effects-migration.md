# LED-Aware Effects Migration Guide

This guide helps developers migrate from the previous effects system to the new LED-aware effects system introduced in BusyLight.

## Overview of Changes

The LED-aware effects system allows targeting specific LEDs on multi-LED devices (like Blink1 mk2) while maintaining full backward compatibility with existing code.

### Key Improvements

1. **LED Targeting**: All effects can now target specific LEDs using the `led` parameter
2. **Unified System**: Removed special-case LED blink implementation - all effects use the same system
3. **API Consistency**: LED parameter is now available across CLI, Web API, and Python API
4. **Backward Compatible**: Existing code continues to work without changes

## Migration Scenarios

### 1. Basic Effect Usage (No Changes Required)

**Before and After - Identical:**
```python
# These work exactly the same as before
controller.all().turn_on("red")
controller.all().blink("blue", count=5)
controller.all().apply_effect(Spectrum())

# CLI commands unchanged
busylight on red
busylight blink blue --count 5
busylight rainbow
```

### 2. LED-Specific Operations (New Capability)

**Before:** LED-specific operations were limited to basic on/blink
```python
# Old: Only basic operations supported LED parameter
controller.all().turn_on("red", led=1)
controller.all().blink("blue", led=2, count=3)

# Effects couldn't target specific LEDs
controller.all().apply_effect(Spectrum())  # Always all LEDs
```

**After:** All effects support LED targeting
```python
# New: All operations and effects support LED parameter
controller.all().turn_on("red", led=1)
controller.all().blink("blue", led=2, count=3)

# Effects can now target specific LEDs
controller.all().apply_effect(Spectrum(), led=1)
controller.all().apply_effect(Gradient((255, 0, 0)), led=2)
```

### 3. CLI Command Enhancements

**Before:** Limited LED support
```bash
# Old: Only basic commands had LED support
busylight on red --led 1
busylight blink blue --led 2 --count 3

# Effects lacked LED support
busylight rainbow           # Always all LEDs
busylight pulse red         # Always all LEDs
```

**After:** All effects support LED targeting
```bash
# Enhanced: All commands support LED targeting
busylight on red --led 1
busylight blink blue --led 2 --count 3

# Effects now support LED targeting
busylight rainbow --led 1
busylight pulse red --led 2 --count 5
busylight fli red blue --led 1 --count 3
```

### 4. Web API Enhancements

**Before:** Limited LED endpoints
```bash
# Old: Only basic operations had LED support
curl "http://localhost:8000/lights/on?color=red&led=1"
curl "http://localhost:8000/lights/blink?color=blue&led=2"

# Effects lacked LED support
curl "http://localhost:8000/lights/rainbow"        # Always all LEDs
curl "http://localhost:8000/lights/pulse?color=red" # Always all LEDs
```

**After:** All endpoints support LED targeting
```bash
# Enhanced: All endpoints support LED parameter
curl "http://localhost:8000/lights/on?color=red&led=1"
curl "http://localhost:8000/lights/blink?color=blue&led=2"

# Effects now support LED targeting
curl "http://localhost:8000/lights/rainbow?led=1"
curl "http://localhost:8000/lights/pulse?color=red&led=2"
curl "http://localhost:8000/lights/fli?color_a=red&color_b=blue&led=1"
```

### 5. Custom Effect Development

**Before:** Effects couldn't handle LED targeting
```python
class MyEffect(BaseEffect):
    async def execute(self, light: "Light", interval: float | None = None) -> None:
        # Old: No LED parameter support
        for color in self.colors:
            light.on(color)  # Always all LEDs
            await asyncio.sleep(interval or self.default_interval)
        light.off()  # Always all LEDs
```

**After:** Effects automatically support LED targeting
```python
class MyEffect(BaseEffect):
    async def execute(self, light: "Light", interval: float | None = None, led: int = 0) -> None:
        # New: LED parameter automatically supported
        for color in self.colors:
            light.on(color, led=led)  # Respects LED targeting
            await asyncio.sleep(interval or self.default_interval)
        light.off(led=led)  # Cleans up specific LED
```

## Breaking Changes

**None!** The migration is fully backward compatible.

### What Doesn't Change

- Existing Python code continues to work unchanged
- Existing CLI commands work exactly the same  
- Existing Web API calls work exactly the same
- Default behavior (all LEDs) remains the same

### What's Enhanced

- All effects can now target specific LEDs via `led` parameter
- More consistent API across all interfaces
- Better multi-LED device support

## Implementation Details

### Effect System Changes

**Unified Architecture:** The new system eliminates the special-case LED blink implementation:

```python
# Before: Two different code paths
if led == 0:
    effect = Effects.for_name("blink")(color, count=count)
    return self.apply_effect(effect, interval=speed_obj.duty_cycle)
else:
    return self._apply_led_blink(color, count, speed_obj.duty_cycle, led)

# After: Single unified path
effect = Effects.for_name("blink")(color, count=count)
return self.apply_effect(effect, interval=speed_obj.duty_cycle, led=led)
```

**BaseEffect Enhancement:** The execute method now includes LED parameter:

```python
async def execute(self, light: "Light", interval: float | None = None, led: int = 0) -> None:
    # LED parameter is now part of the core effect interface
    for color in color_iterator:
        light.on(color, led=led)  # LED targeting built-in
        await asyncio.sleep(sleep_interval)
```

### API Signature Changes

All apply_effect methods now accept LED parameter:

```python
# Controller
def apply_effect(self, effect, duration=None, interval=None, led=0) -> LightSelection

# BusyLightAPI
async def apply_effect(self, effect, light_id=None, led=0) -> None
```

## Migration Checklist

### For Users
- [ ] **No action required** - existing code continues to work
- [ ] **Optional**: Add `--led` parameter to CLI commands for multi-LED targeting
- [ ] **Optional**: Add `led` parameter to Web API calls for LED-specific effects

### For Developers
- [ ] **No action required** - existing Python code continues to work  
- [ ] **Recommended**: Update custom effects to accept `led` parameter in execute method
- [ ] **Optional**: Enhance applications to support multi-LED targeting

### For Custom Effect Authors
- [ ] **Update execute signature** to include `led: int = 0` parameter
- [ ] **Pass LED parameter** to `light.on()` and `light.off()` calls
- [ ] **Test with multi-LED devices** if available

## Examples

### Simple Migration Example

**Before:**
```python
# Your existing code
with LightController() as controller:
    controller.all().turn_on("red")
    controller.all().apply_effect(Spectrum())
```

**After (unchanged - still works):**
```python
# Same code works exactly the same
with LightController() as controller:
    controller.all().turn_on("red")
    controller.all().apply_effect(Spectrum())
```

**Enhanced (new capability):**
```python
# New LED targeting capabilities
with LightController() as controller:
    controller.all().turn_on("red", led=1)      # Top LED red
    controller.all().apply_effect(Spectrum(), led=2)  # Bottom LED rainbow
```

### Custom Effect Migration

**Before:**
```python
class BlinkingGradient(BaseEffect):
    def __init__(self, color):
        self.color = color
        self.priority = TaskPriority.NORMAL
    
    @property
    def colors(self):
        return [self.color, (0, 0, 0)]  # Color + black
    
    @property 
    def default_interval(self):
        return 0.5
```

**After (LED-aware):**
```python
class BlinkingGradient(BaseEffect):
    def __init__(self, color):
        self.color = color
        self.priority = TaskPriority.NORMAL
    
    @property
    def colors(self):
        return [self.color, (0, 0, 0)]  # Color + black
    
    @property 
    def default_interval(self):
        return 0.5
    
    # Optional: Custom execute method with LED support
    async def execute(self, light: "Light", interval: float | None = None, led: int = 0) -> None:
        """Custom execution with LED awareness."""
        try:
            for color in self.colors:
                light.on(color, led=led)  # Pass LED parameter
                await asyncio.sleep(interval or self.default_interval)
        finally:
            light.off(led=led)  # Clean up specific LED
```

## Testing

### Backward Compatibility Tests

All existing functionality is tested to ensure no regressions:

```python
# These tests pass with both old and new systems
def test_backward_compatibility():
    effect = Steady((255, 0, 0))
    mock_light = Mock()
    
    # Old usage still works
    asyncio.run(effect.execute(mock_light))
    mock_light.on.assert_called_with((255, 0, 0), led=0)
```

### New LED Functionality Tests

```python
def test_led_targeting():
    effect = Steady((255, 0, 0))
    mock_light = Mock()
    
    # New LED targeting works
    asyncio.run(effect.execute(mock_light, led=1))
    mock_light.on.assert_called_with((255, 0, 0), led=1)
```

## Support

If you encounter any issues during migration:

1. **Backward Compatibility**: All existing code should work unchanged
2. **New Features**: LED targeting is additive - use `led` parameter when needed
3. **Documentation**: Updated examples show both old and new usage patterns
4. **Testing**: Comprehensive test suite ensures reliability

The LED-aware effects system enhances BusyLight's capabilities while maintaining full compatibility with existing code and usage patterns.
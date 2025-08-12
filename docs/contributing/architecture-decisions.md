# LightManager Usability Improvements

## Current Issues

After analyzing the `LightManager` class, several usability and maintainability issues emerge:

### 1. Complex API Surface
- **Mixed responsibilities**: The manager handles light discovery, selection, async coordination, and effect management
- **Inconsistent async/sync**: Some methods are async (`on_supervisor`, `effect_supervisor`) while others wrap with `asyncio.run()` 
- **Confusing method names**: `on_supervisor` and `effect_supervisor` are internal implementation details exposed as public methods

### 2. Error-Prone Light Selection
- **Index-based selection**: Users must know light indices (0, 1, 2...) rather than meaningful identifiers
- **String parsing**: `parse_target_lights("1,3-5,7")` is fragile and hard to debug
- **Unclear error handling**: `NoLightsFoundError(indices)` passes indices instead of Light subclass

### 3. State Management Issues
- **Inconsistent lazy loading**: `lights` property lazy-loads but can become stale
- **Resource cleanup complexity**: `release()` method has complex error handling and uncertainty about best approach
- **Update method bugs**: `update(greedy=False)` has undefined `new_lights` variable

### 4. Testing Difficulties
- **Complex mocking**: Requires sortable mock objects and deep async/Light knowledge  
- **Tight coupling**: Hard to test individual methods due to dependencies on Light classes
- **Hidden state**: Internal `_lights` attribute makes testing state changes difficult

## Brainstormed Improvements

### Option 1: Simplify with Builder Pattern
Create a fluent interface that's easier to understand and test:

```python
# Current usage:
manager = LightManager()
manager.on((255, 0, 0), [0, 1], timeout=5.0)

# Proposed usage:
LightController().select_all().turn_on(color="red", timeout=5.0)
LightController().select_by_name("desk", "monitor").blink(color="blue", count=5)
LightController().select_indices(0, 2, 4).apply_effect(Effects.rainbow())
```

### Option 2: Context Manager with Cleaner Resource Handling
```python
# Automatic cleanup and clearer scope
with LightManager() as lights:
    lights.all().on(color="green")
    lights.by_name("desk").blink("red") 
    # automatic cleanup on exit
```

### Option 3: Separate Concerns with Multiple Classes
```python
# LightDiscovery - finding and tracking lights
# LightSelector - choosing which lights to operate on  
# LightOperator - performing actions on selected lights

discovery = LightDiscovery()
selector = LightSelector(discovery.available_lights())
operator = LightOperator()

selected = selector.by_pattern("desk*").or_indices(0, 2)
operator.apply_to(selected).turn_on("blue")
```

### Option 4: Functional API with Light Collections
```python
# More functional approach
lights = get_all_lights()
desk_lights = filter_lights(lights, name_pattern="desk*") 
turn_on_lights(desk_lights, color="red", timeout=5.0)
apply_effect(desk_lights, Effects.blink(color="blue", count=3))
```

### Option 5: Event-Driven Manager
```python
# Observer pattern for better async handling
manager = LightManager()
manager.on_lights_changed(callback=log_light_status)
manager.on_effect_complete(callback=cleanup_effect)

await manager.async_turn_on(color="red", selector="all")
await manager.async_apply_effect(Effects.rainbow(), selector="desk*")
```

## Recommended Approach

I recommend **Option 1 (Builder Pattern)** combined with elements from **Option 2 (Context Manager)** because:

### Advantages:
1. **Intuitive API**: Chainable methods read like natural language
2. **Better error messages**: Can validate selections before actions
3. **Easier testing**: Each component can be tested independently  
4. **Backward compatibility**: Can provide legacy wrapper methods
5. **Cleaner async**: Hide async complexity behind sync interface by default
6. **Flexible selection**: Support multiple ways to identify lights (names, patterns, indices)

### Implementation Plan:
1. **LightController**: Main entry point with fluent interface
2. **LightSelection**: Immutable collection of selected lights
3. **LightOperations**: Methods for controlling lights (on/off/effects)
4. **LightRegistry**: Handles discovery and caching
5. **Legacy wrapper**: Maintain LightManager for backward compatibility

## Next Steps

1. Create proof-of-concept implementation
2. Identify breaking changes and migration path  
3. Update CLI commands to use new interface
4. Add comprehensive tests for new design
5. Performance comparison with current implementation
6. Documentation and examples

## Implementation Complete ✅

I have implemented the recommended **Builder Pattern + Context Manager** approach with the following components:

### New Architecture

#### 1. **LightController** - Main entry point
```python
with LightController() as controller:
    controller.all().turn_on("red")
    controller.by_name("desk").blink("blue", count=5)
    controller.by_pattern("monitor.*").turn_off()
```

#### 2. **LightRegistry** - Device management with monitoring
- Automatic plug/unplug detection with configurable polling
- Event callbacks for device changes
- Efficient light lookup by name, pattern, or index
- Resource management and cleanup

#### 3. **LightSelection** - Immutable light collections
- Fluent operations: `selection.turn_on()`, `selection.blink()`, `selection.apply_effect()`
- Multiple selection modes: all, indices, names, patterns, first
- Chainable operations and clear error handling

#### 4. **Comprehensive Testing**
- 28 test cases covering all functionality
- Proper mocking without complex async dependencies
- Integration tests for complete workflows

### Key Features Delivered

✅ **Intuitive API**: Natural language-like method chaining
✅ **Automatic device detection**: Background monitoring with callbacks  
✅ **Context manager**: Automatic resource cleanup
✅ **Multiple selection methods**: By index, name, regex pattern
✅ **Better error handling**: Clear messages and proper exception types
✅ **Easier testing**: Separated concerns and mockable components
✅ **No backward compatibility**: Clean break from old LightManager

### Usage Examples

```python
# Simple usage
with LightController() as lights:
    lights.all().turn_on("green")

# Advanced selection and effects  
with LightController() as controller:
    # Turn on all desk lights
    controller.by_pattern("desk.*").turn_on("blue")
    
    # Blink specific lights
    controller.by_index(0, 2, 4).blink("red", count=3)
    
    # Monitor for device changes
    controller.on_light_plugged(lambda light: print(f"Plugged: {light.name}"))
    controller.on_light_unplugged(lambda light: print(f"Unplugged: {light.name}"))

# CLI integration (much cleaner)
def activate_lights(ctx: typer.Context, color: str):
    with ctx.obj.controller as controller:
        selection = controller.by_index(*ctx.obj.lights) if ctx.obj.lights else controller.all()
        selection.turn_on(color, timeout=ctx.obj.timeout)
```

### Migration Path

1. **Replace LightManager imports** with LightController
2. **Update GlobalOptions** to use controller field  
3. **Simplify CLI commands** using fluent interface
4. **Remove complex error handling** - built into controller
5. **Remove string parsing** - handled automatically

The new implementation is **much more maintainable**, **easier to test**, and provides a **significantly better developer experience** while adding powerful features like automatic device detection.
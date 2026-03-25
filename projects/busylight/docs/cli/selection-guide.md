# Light Selection Methods - Complete Guide

The new LightController provides multiple flexible ways to select which lights to operate on. Here's a comprehensive overview of all selection methods and their use cases.

## Overview of Selection Methods

```python
from busylight.controller import LightController

controller = LightController()

# Selection methods (return LightSelection objects)
controller.select_all()           # All available lights
controller.select_first()         # Just the first light
controller.select_by_indices(0, 2, 4)    # Specific indices
controller.select_by_names("desk", "monitor")  # By exact names  
controller.select_by_pattern(r"desk.*")        # By regex pattern

# Convenience aliases (shorter syntax)
controller.all()                  # Same as select_all()
controller.first()                # Same as select_first()
controller.by_index(0, 2, 4)      # Same as select_by_indices()
controller.by_name("desk")        # Same as select_by_names()
controller.by_pattern(r"desk.*")  # Same as select_by_pattern()
```

## 1. Select All Lights

**When to use**: Operating on all available lights (most common case)

```python
with LightController() as controller:
    # Turn on all lights
    controller.all().turn_on("green")
    
    # Blink all lights 3 times
    controller.all().blink("red", count=3)
    
    # Turn off everything
    controller.all().turn_off()
```

**Details**:
- Returns all currently available lights
- Automatically refreshes light list if empty
- Warns if no lights are found
- Safe to call even with no lights connected

## 2. Select First Light

**When to use**: Simple scenarios, testing, or when you just want "any light"

```python
with LightController() as controller:
    # Quick test - turn first light blue
    controller.first().turn_on("blue")
    
    # Use first light as status indicator
    if system_error:
        controller.first().blink("red", count=10)
```

**Details**:
- Returns the first light in the registry (index 0)
- Returns empty selection if no lights available
- Useful for simple scripts or testing

## 3. Select by Index

**When to use**: When you know the specific position/order of lights

```python
with LightController() as controller:
    # List lights first to see indices
    for i, name in enumerate(controller.list_lights()):
        print(f"{i}: {name}")
    
    # Select specific lights by position
    controller.by_index(0).turn_on("red")           # First light only
    controller.by_index(1, 3).turn_on("blue")       # Second and fourth lights
    controller.by_index(0, 2, 4).blink("green")     # Every other light
```

**Details**:
- Lights are indexed starting from 0
- Invalid indices are ignored with a warning log
- Can select multiple indices at once
- Order doesn't matter: `by_index(3, 1, 0)` works fine

**Example Use Cases**:
```python
# Status lights by position
controller.by_index(0).turn_on("green")    # Status OK
controller.by_index(1).turn_on("yellow")   # Warning
controller.by_index(2).turn_on("red")      # Error

# Physical arrangement (left to right)
controller.by_index(0, 1, 2).turn_on("white")  # Left side lights
controller.by_index(3, 4, 5).turn_off()        # Right side lights
```

## 4. Select by Name

**When to use**: When lights have descriptive names that indicate their purpose or location

```python
with LightController() as controller:
    # Single light by exact name
    controller.by_name("Desk Light").turn_on("warm_white")
    
    # Handle duplicate lights with count parameter
    controller.by_name("Flag").turn_on("blue")           # All Flag lights
    controller.by_name("Flag", count=1).turn_on("red")   # First Flag light
    controller.by_name("Flag", count=2).turn_on("green") # Second Flag light
    
    # Multiple lights by names (different method)
    controller.by_names("Monitor", "Keyboard").turn_on("blue")
    
    # Common naming patterns
    controller.by_name("Status Light").blink("red", count=5)
    controller.by_name("Camera Light").turn_on("green")
```

**Details**:
- Names must match exactly (case-sensitive)
- Unknown names are ignored with warning logs
- **NEW**: Use `count` parameter for duplicate lights (1-based indexing)
- Without `count`: Returns all lights with that name
- With `count`: Returns specific light (e.g., `count=1` for first, `count=2` for second)
- Names are determined by the hardware/driver (e.g., "Blynclight Plus")

**Real Examples** (based on detected lights):
```python
# Actual device names from testing
controller.by_name("MuteMe Original").turn_on("red")
controller.by_name("Blynclight", count=1).turn_on("blue")  # First Blynclight
controller.by_name("Blynclight", count=2).turn_on("green") # Second Blynclight  
controller.by_name("Blink(1)").blink("green")
controller.by_name("fit-statUSB").turn_off()

# Handle multiple lights with same name elegantly
controller.by_name("Flag").turn_on("red")        # Both Flag lights
controller.by_name("Flag", count=1).blink("blue") # Just first Flag
```

## 5. Select by Pattern (Regex)

**When to use**: When you want to select lights based on naming conventions or partial matches

```python
import re

with LightController() as controller:
    # String patterns (case-insensitive by default)
    controller.by_pattern("desk").turn_on("blue")           # Contains "desk"
    controller.by_pattern(".*light").turn_on("white")       # Ends with "light"  
    controller.by_pattern("monitor.*").blink("yellow")      # Starts with "monitor"
    
    # Compiled regex patterns for more control
    pattern = re.compile(r"Blyn.*", re.IGNORECASE)
    controller.by_pattern(pattern).turn_on("purple")
    
    # Complex patterns
    controller.by_pattern(r"(desk|monitor|lamp).*light", re.IGNORECASE).turn_on("cyan")
```

**Details**:
- String patterns are compiled as case-insensitive regex
- Can pass pre-compiled regex objects for more control
- Very powerful for naming conventions
- Returns empty selection if no matches (with warning)

**Advanced Pattern Examples**:
```python
# All USB lights
controller.by_pattern(r".*USB.*").turn_on("green")

# All "Plus" model lights  
controller.by_pattern(r".*Plus$").turn_on("blue")

# Lights with numbers
controller.by_pattern(r".*\(\d+\)").blink("red")  # Matches "Blink(1)"

# Brand-specific patterns
controller.by_pattern(r"^Blyn.*").turn_on("blue")        # Blynclight devices
controller.by_pattern(r"^MuteMe.*").turn_on("orange")    # MuteMe devices
```

## Selection Information and Debugging

```python
with LightController() as controller:
    selection = controller.by_pattern("desk.*")
    
    # Get information about selection
    print(f"Selected {len(selection)} lights")
    print(f"Light names: {selection.names()}")
    print(f"Selection mode: {selection.mode}")
    print(f"Selection criteria: {selection.criteria}")
    
    # Check if selection is empty
    if not selection:
        print("No lights match the criteria")
    else:
        selection.turn_on("green")
```

## Combining Selection with Operations

All selection methods return `LightSelection` objects that support fluent operations:

```python
with LightController() as controller:
    # Chain operations
    controller.by_pattern("desk.*").turn_on("blue").turn_off()
    
    # Store selections for reuse
    work_lights = controller.by_name("Desk Light", "Monitor Light") 
    status_lights = controller.by_index(0, 1)
    
    # Use stored selections
    work_lights.turn_on("white")
    status_lights.blink("green", count=3)
    
    # Operations return LightOperations for further chaining
    controller.all().turn_on("red").turn_off()
```

## Error Handling and Edge Cases

```python
with LightController() as controller:
    # Empty selections don't raise errors - operations are no-ops
    controller.by_name("NonExistent").turn_on("red")  # Logs warning, does nothing
    
    # Invalid indices are skipped
    controller.by_index(999).turn_on("blue")  # Logs warning, does nothing
    
    # No lights available
    if not controller:
        print("No lights detected")
    else:
        controller.all().turn_on("green")
```

## Best Practices

### 1. Use Descriptive Selection Methods
```python
# Good - intention is clear
controller.by_name("Status Light").turn_on("green")
controller.by_pattern("desk.*").turn_on("work_lighting")

# Avoid - requires knowledge of indices
controller.by_index(2).turn_on("green")
```

### 2. Handle Empty Selections Gracefully
```python
# Check selection before complex operations
selection = controller.by_pattern("important.*")
if selection:
    selection.apply_effect(complex_effect)
else:
    print("Important lights not found")
```

### 3. Use Patterns for Naming Conventions
```python
# If you name your lights consistently
controller.by_pattern("room1_.*").turn_on("blue")    # All room 1 lights
controller.by_pattern(".*_status$").blink("red")     # All status lights  
controller.by_pattern("webcam_.*").turn_on("green")  # All webcam lights
```

### 4. Combine Methods for Complex Scenarios
```python
# Status system using different selection methods
def set_system_status(status):
    with LightController() as controller:
        if status == "ok":
            controller.by_pattern("status.*").turn_on("green")
            controller.by_name("Main Monitor").turn_on("blue")
        elif status == "warning":  
            controller.all().turn_off()
            controller.first().blink("yellow", count=3)
        elif status == "error":
            controller.all().blink("red", count=10)
```

## Light Discovery and Enumeration

```python
# Find out what lights are available
with LightController() as controller:
    print(f"Total lights: {len(controller)}")
    
    # List all lights with indices
    for i, name in enumerate(controller.list_lights()):
        print(f"  {i}: {name}")
    
    # Get all lights for manual inspection
    all_lights = controller.registry.get_all_lights()
    for light in all_lights:
        print(f"Light: {light.name}")
        if hasattr(light, 'hardware'):
            print(f"  Hardware: {light.hardware}")
```

This selection system provides tremendous flexibility while keeping the API simple and intuitive. You can start simple with `controller.all()` and get more sophisticated with patterns and names as your lighting setup grows more complex.
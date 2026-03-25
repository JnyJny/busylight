# Multi-LED Device Support

Learn how to control individual LEDs on devices that support multiple
independent light elements.

## Overview

Some USB LED devices contain multiple independent LEDs that can display
different colors simultaneously. BusyLight provides precise control over
these individual LEDs through the `--led` parameter (CLI) or `led` query
parameter (API).

## Supported Multi-LED Devices

### Blink(1) mk2
- **LEDs**: 2 (top and bottom)
- **Indexing**: 1=top, 2=bottom
- **Example**: `busylight on red --led 1` (top LED red)

### BlinkStick Variants

#### BlinkStick Pro
- **LEDs**: 2
- **Indexing**: 1=first, 2=second

#### BlinkStick Square  
- **LEDs**: 8 (arranged in square)
- **Indexing**: 1-8 (clockwise from top-left)

#### BlinkStick Strip
- **LEDs**: Up to 64 (linear strip)
- **Indexing**: 1-64 (left to right)

#### BlinkStick Flex
- **LEDs**: Up to 32 (flexible strip)
- **Indexing**: 1-32 (start to end)

### Luxafor Flag
- **LEDs**: 6 (flag pattern)
- **Indexing**: 1-6 (varies by model)

## LED Parameter Usage

### Default Behavior (led=0)

When no LED is specified, all LEDs on the device display the same color:

```bash
# CLI - all LEDs red
busylight on red

# API - all LEDs red  
curl "http://localhost:8000/light/0/on?color=red"
```

### Specific LED Control (led=1+)

Target individual LEDs by index:

```bash
# CLI examples
busylight on red --led 1      # First LED red
busylight on blue --led 2     # Second LED blue
busylight blink green --led 3 # Third LED blinks green

# API examples
curl "http://localhost:8000/light/0/on?color=red&led=1"
curl "http://localhost:8000/light/0/blink?color=blue&led=2&count=5"
```

## Device-Specific Examples

### Blink(1) mk2 Patterns

```bash
# Status indicator patterns
busylight on green --led 1    # Top: available
busylight on red --led 2      # Bottom: busy

# Meeting status
busylight off                 # Both off: offline
busylight on yellow --led 1   # Top: available
busylight on red --led 2      # Bottom: in meeting

# Build status
busylight blink yellow --led 1 # Top: building
busylight on green --led 2     # Bottom: tests passed
```

### BlinkStick Square (8 LEDs)

```bash
# Progress indicator (fill clockwise)
busylight on green --led 1    # 1/8 complete
busylight on green --led 2    # 2/8 complete
busylight on green --led 3    # 3/8 complete
# ... continue for progress

# Status ring
busylight on red --led 1      # Error at position 1
busylight on green --led 5    # Success at position 5
busylight blink yellow --led 3 # Warning at position 3
```

### BlinkStick Strip (Linear)

```bash
# VU meter effect
for i in {1..8}; do
  busylight on green --led $i
  sleep 0.1
done

# Temperature indicator
busylight on blue --led 1     # Cold (left)
busylight on green --led 5    # Medium (middle)  
busylight on red --led 10     # Hot (right)
```

## Programming Patterns

### Python Multi-LED Control

```python
from busylight_client import BusyLightClient

client = BusyLightClient()

# Blink(1) mk2 dual status
def set_dual_status(top_color, bottom_color):
    """Set different colors on top and bottom LEDs."""
    client.turn_on(0, top_color, led=1)    # Top LED
    client.turn_on(0, bottom_color, led=2) # Bottom LED

# Usage
set_dual_status("green", "red")  # Available but busy
```

### JavaScript LED Animation

```javascript
// BlinkStick Square wave effect
async function waveEffect(lightId, color) {
    for (let led = 1; led <= 8; led++) {
        await client.turnOn(lightId, color, led);
        await new Promise(resolve => setTimeout(resolve, 100));
        await client.turnOff(lightId);
    }
}

waveEffect(0, 'blue');
```

### Shell Script Status Display

```bash
#!/bin/bash
# multi-status.sh - Multi-LED status display

set_build_status() {
    local status="$1"
    
    case "$status" in
        "building")
            busylight blink yellow --led 1  # Top: building
            busylight off --led 2           # Bottom: off
            ;;
        "passed")
            busylight on green --led 1      # Top: success
            busylight on green --led 2      # Bottom: success
            ;;
        "failed")
            busylight on green --led 1      # Top: (last success)
            busylight blink red --led 2     # Bottom: failed
            ;;
        "stopped")
            busylight off                   # Both off
            ;;
    esac
}

# Usage
set_build_status "building"
# ... run build ...
set_build_status "passed"
```

## LED Indexing Reference

### General Rules
- **LED 0**: All LEDs (default behavior)
- **LED 1+**: Specific LEDs (1-based indexing)
- **Invalid indices**: Ignored (no error, no effect)
- **Single-LED devices**: LED parameter ignored

### Device-Specific Indexing

| Device | LED Count | Index Range | Layout |
|--------|-----------|-------------|---------|
| Blink(1) mk2 | 2 | 1-2 | 1=top, 2=bottom |
| BlinkStick Pro | 2 | 1-2 | Linear |
| BlinkStick Square | 8 | 1-8 | Clockwise from top-left |
| BlinkStick Strip | 1-64 | 1-64 | Left to right |
| BlinkStick Flex | 1-32 | 1-32 | Start to end |
| Luxafor Flag | 6 | 1-6 | Flag pattern |

## Advanced Techniques

### LED State Management

```python
class LEDStateManager:
    def __init__(self, client, light_id):
        self.client = client
        self.light_id = light_id
        self.led_states = {}
    
    def set_led(self, led_index, color):
        """Set LED color and track state."""
        self.client.turn_on(self.light_id, color, led=led_index)
        self.led_states[led_index] = color
    
    def get_state(self, led_index):
        """Get current LED color."""
        return self.led_states.get(led_index, "off")
    
    def clear_all(self):
        """Turn off all LEDs."""
        self.client.turn_off_all()
        self.led_states.clear()

# Usage
manager = LEDStateManager(client, 0)
manager.set_led(1, "red")
manager.set_led(2, "green")
print(manager.get_state(1))  # "red"
```

### Pattern Sequences

```bash
#!/bin/bash
# led-patterns.sh

# Knight Rider effect (BlinkStick Strip)
knight_rider() {
    local max_led=8
    
    # Forward sweep
    for i in $(seq 1 $max_led); do
        busylight on red --led $i
        sleep 0.1
        busylight off --led $i
    done
    
    # Backward sweep
    for i in $(seq $max_led -1 1); do
        busylight on red --led $i
        sleep 0.1
        busylight off --led $i
    done
}

# Breathing effect (all LEDs)
breathing_effect() {
    local color="$1"
    
    for brightness in 0.1 0.3 0.5 0.8 1.0 0.8 0.5 0.3 0.1; do
        busylight --dim $brightness on $color
        sleep 0.2
    done
}
```

## Troubleshooting Multi-LED Issues

### LED Not Responding
1. **Check LED index**: Verify index is within device range
2. **Test all LEDs**: Use `led=0` to confirm device works
3. **Check device model**: Ensure device supports multiple LEDs
4. **Debug output**: Use `--debug` flag for detailed information

### Inconsistent Behavior
1. **LED conflicts**: Ensure no overlapping LED commands
2. **Device limitations**: Some devices have LED interdependencies  
3. **Timing issues**: Add delays between rapid LED changes
4. **Power limitations**: High LED counts may have power constraints

### Performance Considerations
- **Batch operations**: Group LED changes when possible
- **Avoid rapid updates**: Some devices have update rate limits
- **Power management**: Multiple LEDs consume more power
- **USB bandwidth**: Very high LED counts may need update throttling

Multi-LED support enables sophisticated status displays and visual effects
that would be impossible with single-LED devices.
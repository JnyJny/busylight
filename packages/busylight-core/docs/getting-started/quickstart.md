# Quick Start

This guide will help you get started with Busylight Core quickly.

## Installation

First, install busylight_core using pip:

```bash
pip install busylight_core
```

Or with uv:

```bash
uv add busylight_core
```

## Basic Usage

After [installing](installation.md) busylight_core, you can start controlling lights in your Python code:

**Any compatible device (recommended for simple use cases):**

```python
from busylight_core import Light, NoLightsFoundError

try:
    light = Light.first_light()
    light.on((255, 0, 0))  # Turn on red
    light.off()             # Turn off
except NoLightsFoundError:
    print("No compatible lights found. Check your device connection.")
```

**Vendor-specific devices (recommended for vendor-specific features):**

```python
from busylight_core import EmbravaLights, KuandoLights, NoLightsFoundError

# Embrava devices support dim/bright and flash
try:
    light = EmbravaLights.first_light()
    light.on((255, 0, 0))
    light.dim()       # Reduce brightness
    light.bright()    # Restore full brightness
    light.flash((255, 255, 0))  # Flash yellow
except NoLightsFoundError:
    print("No Embrava devices found")

# Kuando devices manage keepalive automatically
try:
    light = KuandoLights.first_light()
    light.on((0, 255, 0))  # Keepalive starts automatically
except NoLightsFoundError:
    print("No Kuando devices found")
```

## Discovering Your Device

**Check all connected devices:**

```python
from busylight_core import Light

lights = Light.all_lights()

if lights:
    for i, light in enumerate(lights):
        print(f"Light {i}: {light.vendor()} {light.name}")
        print(f"  Hardware: {light.hardware.manufacturer_string}")
        print(f"  Path: {light.path}")
else:
    print("No lights found. Try:")
    print("1. Check USB connection")
    print("2. On Linux, ensure udev rules are configured")
    print("3. Try running with sudo (not recommended for production)")
```

**Check devices by vendor:**

```python
from busylight_core import (
    EmbravaLights, KuandoLights, LuxaforLights,
    AgileInnovativeLights, ThingMLights, MuteMeLights
)

vendors = [
    ("Embrava", EmbravaLights),
    ("Kuando", KuandoLights),
    ("Luxafor", LuxaforLights),
    ("BlinkStick", AgileInnovativeLights),
    ("ThingM", ThingMLights),
    ("MuteMe", MuteMeLights),
]

for vendor_name, vendor_class in vendors:
    devices = vendor_class.all_lights()
    if devices:
        print(f"{vendor_name}: {len(devices)} device(s)")
        for device in devices:
            print(f"  - {device.name}")
```

## Basic Light Control

### Colors

```python
from busylight_core import Light, NoLightsFoundError

try:
    light = Light.first_light()

    # Basic colors (RGB tuples, values 0-255)
    light.on((255, 0, 0))      # Red
    light.on((0, 255, 0))      # Green
    light.on((0, 0, 255))      # Blue
    light.on((255, 255, 0))    # Yellow
    light.on((255, 0, 255))    # Magenta
    light.on((0, 255, 255))    # Cyan
    light.on((255, 255, 255))  # White

    # Turn off
    light.off()

    # Check if light is on
    if light.is_lit:
        print("Light is currently on")

except NoLightsFoundError:
    print("No lights available")
```

### Flash Patterns (Embrava Only)

Only Embrava Blynclight devices have hardware flash support:

```python
from busylight_core import EmbravaLights, NoLightsFoundError
from busylight_core.vendors.embrava.implementation import FlashSpeed

try:
    light = EmbravaLights.first_light()

    # Flash with default speed (slow)
    light.flash((255, 0, 0))

    # Flash with specific speed
    light.flash((255, 165, 0), speed=FlashSpeed.slow)

    # Stop flashing, return to solid color
    light.stop_flashing()

except NoLightsFoundError:
    print("No Embrava devices found")
```

For devices without hardware flash, implement it in software:

```python
import time
from busylight_core import Light, NoLightsFoundError

try:
    light = Light.first_light()

    # Software flash fallback
    for _ in range(3):
        light.on((255, 0, 0))
        time.sleep(0.5)
        light.off()
        time.sleep(0.5)

except NoLightsFoundError:
    print("No lights available")
```

## Device Compatibility

Different devices have different capabilities. See [Device Capabilities](../user-guide/device-capabilities.md) for a full breakdown of what each device supports.

## Configuration

Busylight Core can be configured at initialization time. See [Configuration](configuration.md) for details.

## Next Steps

- Learn about specific device capabilities: [Device Capabilities](../user-guide/device-capabilities.md)
- See comprehensive examples: [Examples](../user-guide/examples.md)
- Check out the [API Reference](../reference/index.md)

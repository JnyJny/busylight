# Examples

This page provides comprehensive examples of using Busylight Core for various scenarios.

## Basic Device Control

### Finding and Connecting to Lights

```python
from busylight_core import Light, NoLightsFoundError

# Get all available lights
lights = Light.all_lights()
print(f"Found {len(lights)} light(s)")

# Get the first available light
try:
    light = Light.first_light()
    print(f"Using: {light.vendor()} {light.name}")
except NoLightsFoundError:
    print("No lights found")

# Find lights by vendor
embrava_lights = [l for l in lights if l.vendor() == "Embrava"]
```

### Basic Light Operations

```python
from busylight_core import Light, NoLightsFoundError

try:
    light = Light.first_light()

    # Turn on with different colors
    light.on((255, 0, 0))    # Red
    light.on((0, 255, 0))    # Green
    light.on((0, 0, 255))    # Blue
    light.on((255, 255, 0))  # Yellow

    # Turn off
    light.off()

    # Check state
    print(f"Color: {light.color}")
    print(f"Is lit: {light.is_lit}")

except NoLightsFoundError:
    print("No lights found")
```

## Vendor-Specific Examples

### Embrava Blynclight - Flash and Brightness

```python
from busylight_core import EmbravaLights, NoLightsFoundError
from busylight_core.vendors.embrava.implementation import FlashSpeed

try:
    light = EmbravaLights.first_light()

    # Solid color
    light.on((255, 0, 0))

    # Dim and restore
    light.dim()
    light.bright()

    # Flash with default speed
    light.flash((255, 255, 0))

    # Flash with explicit speed
    light.flash((255, 0, 0), speed=FlashSpeed.slow)

    # Stop flashing
    light.stop_flashing()

    # Turn off
    light.off()

except NoLightsFoundError:
    print("No Embrava devices found")
```

### Embrava Blynclight Plus - Audio

```python
from busylight_core import BlynclightPlus, NoLightsFoundError

try:
    light = BlynclightPlus.first_light()

    # Turn on with color
    light.on((255, 0, 0))

    # Play a sound (music track 0-7, volume 0-3)
    light.play_sound(music=0, volume=2, repeat=False)

    # Mute/unmute
    light.mute()
    light.unmute()

    # Stop sound
    light.stop_sound()

    light.off()

except NoLightsFoundError:
    print("No Blynclight Plus devices found")
```

### Kuando Busylight - Basic Usage

```python
from busylight_core import KuandoLights, BusylightOmega, NoLightsFoundError

# Any Kuando device
try:
    light = KuandoLights.first_light()
    light.on((0, 255, 0))   # Keepalive managed automatically
    # ... light stays on ...
    light.off()              # Keepalive cancelled automatically
except NoLightsFoundError:
    print("No Kuando devices found")

# Specific Omega devices only
try:
    omega = BusylightOmega.first_light()
    omega.on((0, 0, 255))
    omega.off()
except NoLightsFoundError:
    print("No Omega devices found")
```

### Luxafor Flag - Multi-LED Control

```python
from busylight_core import Flag, NoLightsFoundError

try:
    flag = Flag.first_light()

    # Control individual LEDs (Flag has 6 LEDs)
    flag.on((255, 0, 0), led=1)    # LED 1 red
    flag.on((0, 255, 0), led=2)    # LED 2 green
    flag.on((0, 0, 255), led=3)    # LED 3 blue

    # All LEDs same color (led=0 means all)
    flag.on((255, 255, 255))

    flag.off()

except NoLightsFoundError:
    print("No Luxafor Flag devices found")
```

### BlinkStick - Multi-LED Control

```python
from busylight_core import BlinkStickSquare, BlinkStickPro, NoLightsFoundError

# BlinkStick Square has 8 LEDs
try:
    square = BlinkStickSquare.first_light()
    colors = [(255,0,0), (255,127,0), (255,255,0), (0,255,0),
              (0,0,255), (75,0,130), (148,0,211), (255,255,255)]
    for i, color in enumerate(colors):
        square.on(color, led=i)
except NoLightsFoundError:
    pass

# BlinkStick Pro has 64 LEDs
try:
    pro = BlinkStickPro.first_light()
    pro.on((255, 0, 0), led=0)
    pro.on((0, 255, 0), led=1)
except NoLightsFoundError:
    pass
```

### MuteMe - Button Input

```python
from busylight_core import MuteMe, MuteMeLights, NoLightsFoundError

try:
    device = MuteMe.first_light()

    # Check button capability and state
    if device.is_button:
        if device.button_on:
            print("Button is pressed")
            device.on((255, 0, 0))  # Red = muted
        else:
            print("Button is not pressed")
            device.on((0, 255, 0))  # Green = unmuted

except NoLightsFoundError:
    print("No MuteMe devices found")
```

## Task Management

### Periodic Tasks (Non-Asyncio)

```python
import time
from busylight_core import Light, NoLightsFoundError

try:
    light = Light.first_light()

    # Task function receives the light instance
    def pulse(light):
        if light.is_lit:
            light.off()
        else:
            light.on((0, 128, 255))

    # Start periodic task (uses threading.Timer automatically)
    light.add_task("pulse", pulse, interval=0.5)
    time.sleep(5)
    light.cancel_task("pulse")
    light.off()

except NoLightsFoundError:
    print("No lights found")
```

### Periodic Tasks (Asyncio)

```python
import asyncio
from busylight_core import Light, NoLightsFoundError

async def main():
    try:
        light = Light.first_light()

        async def color_cycle(light):
            colors = [(255,0,0), (0,255,0), (0,0,255)]
            for color in colors:
                light.on(color)
                await asyncio.sleep(0.3)

        # In asyncio context, automatically uses asyncio.Task
        light.add_task("cycle", color_cycle, interval=1.0)
        await asyncio.sleep(10)
        light.cancel_tasks()
        light.off()

    except NoLightsFoundError:
        print("No lights found")

asyncio.run(main())
```

## Error Handling and Debugging

### Robust Error Handling

```python
from busylight_core import Light, LightUnavailableError, NoLightsFoundError

try:
    light = Light.first_light()
    light.on((255, 0, 0))
except NoLightsFoundError:
    print("No busylights found. Please connect a device.")
except LightUnavailableError as error:
    print(f"Light unavailable: {error}")
except Exception as error:
    print(f"Unexpected error: {error}")
```

### Debugging Device Issues

```python
from loguru import logger
from busylight_core import Light, Hardware

# Enable debug logging
logger.enable("busylight_core")

# Check hardware detection
hardware_devices = Hardware.enumerate()
print(f"Found {len(hardware_devices)} hardware devices:")

for hw in hardware_devices:
    print(f"  {hw.manufacturer_string} {hw.product_string}")
    print(f"    VID:PID = {hw.vendor_id:04x}:{hw.product_id:04x}")
    print(f"    Path: {hw.path}")

# Check light recognition
lights = Light.all_lights()
print(f"Recognized {len(lights)} as lights:")

for light in lights:
    print(f"  {light.vendor()} {light.name}")
    print(f"    Class: {light.__class__.__name__}")

logger.disable("busylight_core")
```

## Next Steps

- Learn more about the [API Reference](../reference/index.md)
- Check out [Device Capabilities](device-capabilities.md) for device-specific features
- Read the [Contributing Guide](../contributing.md) to add support for new devices

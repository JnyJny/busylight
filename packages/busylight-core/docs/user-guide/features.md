# Features

Busylight Core provides functionality for controlling USB status lights programmatically.

## Device Discovery and Management

### Automatic Device Detection

Busylight Core automatically detects and recognizes supported devices:

```python
from busylight_core import Light, Hardware, NoLightsFoundError

# Low-level hardware discovery
hardware_devices = Hardware.enumerate()
print(f"Found {len(hardware_devices)} hardware devices")

# High-level light discovery
lights = Light.all_lights()
print(f"Recognized {len(lights)} busylights")
```

### Device Information

Get detailed information about connected devices:

```python continuation
for light in Light.all_lights():
    print(f"Vendor: {light.vendor()}")
    print(f"Model: {light.name}")
    print(f"Path: {light.path}")
    print(f"Hardware: {light.hardware.manufacturer_string}")
    print(f"Device ID: {light.hardware.device_id}")
```

## Color Management

### Color Format

Busylight Core uses RGB color tuples with integer values from 0-255:

```python continuation
try:
    light = Light.first_light()

    # RGB tuples (0-255) - only supported format
    light.on((255, 0, 0))      # Red
    light.on((0, 255, 0))      # Green
    light.on((0, 0, 255))      # Blue
    light.on((255, 255, 0))    # Yellow
    light.on((255, 0, 255))    # Magenta
    light.on((0, 255, 255))    # Cyan
    light.on((255, 255, 255))  # White
    light.on((128, 128, 128))  # Gray (50% brightness)

    # Turn off
    light.off()

    # Check state
    print(f"Color: {light.color}")
    print(f"Is lit: {light.is_lit}")

except NoLightsFoundError:
    print("No lights available")
```

## Vendor-Specific Features

Different vendors provide different capabilities beyond basic color control. These features are only available on the specific device classes listed.

### Multi-LED Devices (BlinkStick, Luxafor Flag)

Some devices have multiple individually addressable LEDs. Use the `led` parameter on `on()`:

```python
from busylight_core import Flag, BlinkStickSquare, NoLightsFoundError

# Luxafor Flag has 6 LEDs
try:
    flag = Flag.first_light()
    flag.on((255, 0, 0), led=0)    # First LED red
    flag.on((0, 255, 0), led=1)    # Second LED green
    flag.on((0, 0, 255), led=2)    # Third LED blue
    flag.on((255, 255, 0))         # led=0 targets all LEDs
except NoLightsFoundError:
    pass

# BlinkStick Square has 8 LEDs
try:
    square = BlinkStickSquare.first_light()
    square.on((255, 0, 0), led=0)
    square.on((0, 255, 0), led=1)
except NoLightsFoundError:
    pass
```

The `led` parameter is accepted by all devices (it's part of the base `on()` signature), but only multi-LED devices use it meaningfully. Single-LED devices ignore it.

### Audio (Embrava Blynclight Plus Only)

Only the `BlynclightPlus` has audio playback:

```python
from busylight_core import BlynclightPlus, NoLightsFoundError

try:
    light = BlynclightPlus.first_light()

    # Play a sound (music: 0-7, volume: 0-3)
    light.play_sound(music=0, volume=1, repeat=False)

    # Stop sound
    light.stop_sound()

    # Mute/unmute
    light.mute()
    light.unmute()

except NoLightsFoundError:
    print("No Blynclight Plus devices found")
```

**Note:** The `Blynclight` and `BlynclightMini` do NOT have audio support. Only the `BlynclightPlus` class exposes `play_sound()`, `stop_sound()`, `mute()`, and `unmute()`.

### Flash Patterns (Embrava Only)

Only Embrava devices (`Blynclight`, `BlynclightMini`, `BlynclightPlus`) support hardware flash:

```python
from busylight_core import EmbravaLights, NoLightsFoundError
from busylight_core.vendors.embrava.implementation import FlashSpeed

try:
    light = EmbravaLights.first_light()

    # Flash with default speed
    light.flash((255, 0, 0))

    # Flash with explicit speed
    light.flash((255, 255, 0), speed=FlashSpeed.slow)

    # Stop flashing
    light.stop_flashing()

except NoLightsFoundError:
    print("No Embrava devices found")
```

### Brightness Control (Embrava Only)

```python
from busylight_core import EmbravaLights, NoLightsFoundError

try:
    light = EmbravaLights.first_light()
    light.on((255, 0, 0))
    light.dim()       # Reduce brightness
    light.bright()    # Restore full brightness
except NoLightsFoundError:
    pass
```

### Button Input (MuteMe, Luxafor Mute)

Some devices have physical buttons. Check for button support using `is_button`:

```python
from busylight_core import MuteMe, NoLightsFoundError

try:
    device = MuteMe.first_light()

    if device.is_button:
        if device.button_on:
            print("Button is currently pressed")
            device.on((255, 0, 0))  # Red when pressed
        else:
            device.on((0, 255, 0))  # Green when not pressed

except NoLightsFoundError:
    print("No MuteMe devices found")
```

**Properties:**
- `is_button` - `True` if the device has a physical button
- `button_on` - `True` if the button is currently pressed

These are available on `MuteMe`, `MuteMeMini`, `MuteSync`, and `Mute` (Luxafor Mute).

### Kuando Keepalive

Kuando Busylight devices (Alpha, Omega) require periodic keepalive packets to stay active. This is handled automatically -- when you call `on()`, a keepalive task starts. When you call `off()`, it stops. You do not need to manage keepalive manually.

```python
from busylight_core import KuandoLights, NoLightsFoundError

try:
    light = KuandoLights.first_light()
    light.on((0, 255, 0))   # Keepalive starts automatically
    # ... light stays on ...
    light.off()              # Keepalive stops automatically
except NoLightsFoundError:
    pass
```

**Note on Kuando ringtones:** The Kuando protocol supports ringtones (9 tones plus off) and volume control at the command level, but this is not currently exposed through the public `on()` API. If you need ringtone support, you would need to work with the low-level `Step.jump()` command directly (see `busylight_core.vendors.kuando.implementation.commands`).

## Task Management

Every Light instance includes task management that automatically adapts to your environment (asyncio or threading):

```python
import time
from busylight_core import Light, NoLightsFoundError

try:
    light = Light.first_light()

    # Define a task function (receives the light as argument)
    def blink(light):
        if light.is_lit:
            light.off()
        else:
            light.on((255, 0, 0))

    # Add a periodic task
    light.add_task("blink", blink, interval=1.0)

    time.sleep(5)  # Let it blink for 5 seconds

    # Cancel specific task
    light.cancel_task("blink")

    # Or cancel all tasks
    light.cancel_tasks()

except NoLightsFoundError:
    print("No lights found")
```

### Asyncio Context

```python
import asyncio
from busylight_core import Light, NoLightsFoundError

async def main():
    try:
        light = Light.first_light()

        async def fade(light):
            for brightness in range(0, 256, 16):
                light.on((brightness, 0, 0))
                await asyncio.sleep(0.1)

        light.add_task("fade", fade, interval=3.0)
        await asyncio.sleep(10)
        light.cancel_tasks()

    except NoLightsFoundError:
        print("No lights found")

asyncio.run(main())
```

In asyncio contexts, tasks use `asyncio.Task`. In non-asyncio contexts, they use `threading.Timer`. The selection is automatic.

## Error Handling

### Exception Types

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

### Hardware Debugging

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

# Disable logging when done
logger.disable("busylight_core")
```

## Next Steps

- Learn more about the [API Reference](../reference/index.md)
- Check out device-specific capabilities in [Device Capabilities](device-capabilities.md)
- Visit the [GitHub repository](https://github.com/JnyJny/busylight_core) for the latest updates

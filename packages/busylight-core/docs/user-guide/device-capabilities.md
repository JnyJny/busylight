# Device Capabilities Reference

This guide provides detailed information about each supported device's capabilities.

## Capability Overview

| Feature | Devices | Description |
|---------|---------|-------------|
| **Basic RGB Color** | All devices | `on(color)` / `off()` with RGB tuples (0-255) |
| **Hardware Flash** | Embrava (3 devices) | `flash(color, speed)` with `FlashSpeed` enum |
| **Dim/Bright** | Embrava (3 devices) | `dim()` / `bright()` for brightness control |
| **Audio Playback** | Blynclight Plus (1 device) | `play_sound(music, volume, repeat)` |
| **Multi-LED Control** | BlinkStick variants, Luxafor Flag | `on(color, led=N)` for individual LEDs |
| **Button Input** | MuteMe (3 devices), Luxafor Mute | `is_button` / `button_on` properties |
| **Auto Keepalive** | Kuando (2 devices) | Managed automatically by `on()` / `off()` |

## Vendor Details

### Embrava (3 devices)

Professional meeting status lights with flash, brightness, and audio capabilities.

| Device | Flash | Dim/Bright | Audio | Special |
|--------|-------|------------|-------|---------|
| **Blynclight** | Yes | Yes | No | Industry standard |
| **Blynclight Mini** | Yes | Yes | No | Compact form |
| **Blynclight Plus** | Yes | Yes | Yes | `play_sound()`, `mute()`, `unmute()` |

**Usage:**
```python
from busylight_core import EmbravaLights, BlynclightPlus, NoLightsFoundError

# Any Embrava device - flash and brightness
try:
    light = EmbravaLights.first_light()
    light.on((255, 0, 0))
    light.dim()
    light.bright()
    light.flash((255, 255, 0))
    light.stop_flashing()
except NoLightsFoundError:
    pass

# Blynclight Plus only - audio
try:
    light = BlynclightPlus.first_light()
    light.play_sound(music=0, volume=2)
    light.stop_sound()
    light.mute()
    light.unmute()
except NoLightsFoundError:
    pass
```

### Kuando (2 devices)

Nordic-design status lights with automatic keepalive management.

| Device | Flash | Audio | Special |
|--------|-------|-------|---------|
| **Busylight Alpha** | No | No | Multiple USB IDs, auto keepalive |
| **Busylight Omega** | No | No | Premium model, auto keepalive |

**Usage:**
```python
from busylight_core import KuandoLights, BusylightAlpha, NoLightsFoundError

try:
    light = KuandoLights.first_light()
    light.on((0, 255, 0))   # Keepalive starts automatically
    light.off()              # Keepalive stops automatically
except NoLightsFoundError:
    pass
```

**Note on ringtones:** The Kuando protocol supports 9 built-in ringtones (`Ring` enum: OpenOffice, Quiet, Funky, FairyTale, KuandoTrain, TelephoneNordic, TelephoneOriginal, TelephonePickMeUp, Buzz) with volume control (0-3) at the command level. However, these are **not exposed through the public `on()` API**. The `Step.jump()` command in `busylight_core.vendors.kuando.implementation.commands` accepts `ringtone` and `volume` parameters for direct protocol access.

### Luxafor (5 devices)

Versatile devices including multi-LED and button-equipped models.

| Device | LEDs | Flash | Button | Special |
|--------|------|-------|--------|---------|
| **Flag** | 6 | No | No | Multi-LED control via `led` param |
| **Orb** | 1 | No | No | Spherical design |
| **Bluetooth** | 1 | No | No | Wireless capable |
| **Mute** | 1 | No | Yes | `is_button`, `button_on` |
| **Busy Tag** | 1 | No | No | ASCII text protocol |

**Usage:**
```python
from busylight_core import Flag, NoLightsFoundError
from busylight_core.vendors.luxafor import Mute

# Multi-LED with Flag
try:
    flag = Flag.first_light()
    for i in range(6):
        flag.on((255, 0, 0), led=i)  # Individual LED control
    flag.on((0, 255, 0))             # All LEDs (led=0 default)
except NoLightsFoundError:
    pass

# Button with Luxafor Mute
try:
    mute = Mute.first_light()
    if mute.is_button and mute.button_on:
        mute.on((255, 0, 0))  # Red when pressed
except NoLightsFoundError:
    pass
```

### Agile Innovative BlinkStick (6 variants)

Flexible multi-LED strips and matrices for creative applications.

| Device | LEDs | Special |
|--------|------|---------|
| **BlinkStick** | 1 | Basic model |
| **BlinkStick Nano** | 2 | Dual LED |
| **BlinkStick Square** | 8 | 8-LED matrix |
| **BlinkStick Strip** | 8 | LED strip |
| **BlinkStick Flex** | 32 | Flexible strip |
| **BlinkStick Pro** | 64 | Professional strip |

**Usage:**
```python
from busylight_core import AgileInnovativeLights, BlinkStickPro, NoLightsFoundError

# Any BlinkStick
try:
    light = AgileInnovativeLights.first_light()
    light.on((255, 0, 255))
except NoLightsFoundError:
    pass

# Multi-LED with BlinkStick Pro
try:
    strip = BlinkStickPro.first_light()
    colors = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255)]
    for i, color in enumerate(colors):
        strip.on(color, led=i)
except NoLightsFoundError:
    pass
```

### ThingM (1 device)

Popular maker-friendly device with dual LEDs.

| Device | LEDs | Special |
|--------|------|---------|
| **Blink(1)** | 2 | Dual LED control |

**Usage:**
```python
from busylight_core import Blink1, NoLightsFoundError

try:
    blink = Blink1.first_light()
    blink.on((255, 0, 0), led=0)  # First LED
    blink.on((0, 0, 255), led=1)  # Second LED
    blink.on((255, 255, 255))     # Both LEDs
except NoLightsFoundError:
    pass
```

### MuteMe (3 devices)

Specialized mute button devices with status indication.

| Device | Button | Special |
|--------|--------|---------|
| **MuteMe Original** | Yes | `is_button`, `button_on` |
| **MuteMe Mini** | Yes | Compact form |
| **MuteSync Button** | Yes | `is_button`, `button_on` |

**Usage:**
```python
from busylight_core import MuteMe, MuteMeLights, NoLightsFoundError

try:
    device = MuteMe.first_light()
    if device.is_button:
        if device.button_on:
            device.on((255, 0, 0))  # Red when muted
        else:
            device.on((0, 255, 0))  # Green when unmuted
except NoLightsFoundError:
    pass
```

### Other Vendors

**EPOS Busylight** - Professional conferencing light
```python
from busylight_core import EPOSLights, NoLightsFoundError

try:
    light = EPOSLights.first_light()
    light.on((0, 255, 0))
except NoLightsFoundError:
    pass
```

**Plantronics Status Indicator** - Call center indicator
```python
from busylight_core import PlantronicsLights, NoLightsFoundError

try:
    light = PlantronicsLights.first_light()
    light.on((255, 0, 0))
except NoLightsFoundError:
    pass
```

**CompuLab fit-statUSB** - Industrial status indicator
```python
from busylight_core import CompuLabLights, NoLightsFoundError

try:
    light = CompuLabLights.first_light()
    light.on((255, 165, 0))
except NoLightsFoundError:
    pass
```

## Hardware Notes

### Color Ordering

Devices use different internal color byte orders, but the library handles all conversions automatically. You always pass standard RGB tuples:

- BlinkStick devices: GRB ordering internally
- Blynclight devices: RBG ordering internally
- Kuando Busylight devices: RGB with 0-100 scaling internally

### Power Requirements

All supported devices are USB bus-powered and require no external power supply.

### Platform Compatibility

All devices work on Windows, macOS, and Linux. Linux users need udev rules for non-root access (see [Installation Guide](../getting-started/installation.md#linux-setup-udev-rules)).

## Next Steps

- Check the [Examples](examples.md) for more usage patterns
- Review the [API Reference](../reference/index.md) for complete method documentation
- See [Installation Guide](../getting-started/installation.md) for setup instructions

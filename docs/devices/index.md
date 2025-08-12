# Supported Devices

BusyLight supports 23 USB LED devices from 9 vendors. This page provides
compatibility information and setup instructions for each device type.

## Compatibility Matrix

| Vendor | Models | LED Support | Platform Notes |
|--------|---------|-------------|----------------|
| [**Agile Innovative**](#agile-innovative) | BlinkStick variants | Multi-LED targeting | Full support |
| [**Compulab**](#compulab) | fit-statUSB | Single LED | Full support |
| [**EPOS**](#epos) | Busylight | Single LED | Full support |
| [**Embrava**](#embrava) | Blynclight variants | Single LED | Full support |
| [**Kuando**](#kuando) | Busylight Alpha, Omega | Single LED | Keepalive required |
| [**Luxafor**](#luxafor) | Flag, Orb, Mute variants | Multi/Single LED | Model-dependent |
| [**Plantronics**](#plantronics) | Status Indicator | Single LED | Full support |
| [**MuteMe**](#muteme) | Original, Mini, MuteSync | Single LED | Full support |
| [**ThingM**](#thingm) | Blink(1), Blink(1) mk2 | mk2: Multi-LED | Full support |

## LED Support Types

### Single LED Devices
Most devices have a single LED that displays one color at a time. The `led`
parameter is ignored for these devices.

### Multi-LED Devices  
Some devices have multiple independent LEDs that can display different
colors simultaneously:

- **Blink(1) mk2**: 2 LEDs (top and bottom)
- **BlinkStick variants**: 1-64 LEDs depending on model
- **Luxafor Flag**: 6 LEDs in flag pattern

## Vendor Details

### Agile Innovative

**BlinkStick Series** - USB LED controllers with various form factors.

**Models:**
- BlinkStick (single LED)
- BlinkStick Pro (2 LEDs)
- BlinkStick Square (8 LEDs)  
- BlinkStick Strip (up to 64 LEDs)
- BlinkStick Nano (single LED)
- BlinkStick Flex (32 LEDs)

**LED Control:**
```bash
# Single LED models
busylight on red

# Multi-LED models
busylight on red --led 1    # First LED
busylight on blue --led 8   # Eighth LED (Square)
```

**Platform Support:** macOS, Linux, Windows (experimental)

### Compulab

**fit-statUSB** - Compact USB status light.

**Features:**
- Single RGB LED
- Compact form factor
- Low power consumption

**Platform Support:** macOS, Linux

### EPOS

**Busylight** - Professional presence indicator.

**Features:**
- Single RGB LED
- Professional design
- USB powered

**Platform Support:** macOS, Linux

### Embrava

**Blynclight Series** - Professional presence lights.

**Models:**
- Blynclight (original)
- Blynclight Mini (compact)
- Blynclight Plus (enhanced brightness)

**Features:**
- Single RGB LED per device
- Professional appearance
- Stable USB connection

**Platform Support:** macOS, Linux

### Kuando

**Busylight Series** - Professional status lights with unique keepalive
requirement.

**Models:**
- Busylight Alpha
- Busylight Omega

**Special Requirements:**
Kuando devices require keepalive tasks to maintain USB connection. The CLI
handles this automatically by keeping the process running:

```bash
# This will run continuously for Kuando lights
busylight on red
# Press Ctrl+C to stop
```

**Platform Support:** macOS, Linux

### Luxafor

**Multi-purpose LED indicators** with various form factors.

**Models:**
- Flag (6 LEDs in flag pattern)
- Orb (single LED)
- Mute (single LED)
- Busy Tag (wearable, single LED)
- Bluetooth variants

**LED Control for Flag:**
```bash
# Control all LEDs
busylight on red

# Control specific LED (Flag model)
busylight on red --led 1    # Top LED
busylight on blue --led 6   # Bottom right LED
```

**Platform Support:** macOS, Linux

### Plantronics

**Status Indicator** - Simple presence light.

**Features:**
- Single RGB LED
- Minimal design
- Reliable operation

**Platform Support:** macOS, Linux

### MuteMe

**Mute Status Indicators** - Meeting mute status lights.

**Models:**
- MuteMe Original
- Mute Mini  
- MuteSync

**Features:**
- Single RGB LED
- Meeting-focused design
- USB powered

**Platform Support:** macOS, Linux

### ThingM

**Blink(1) Series** - Original USB notification lights.

**Models:**
- Blink(1) (original, single LED)
- Blink(1) mk2 (2 independent LEDs)

**LED Control for mk2:**
```bash
# Control both LEDs
busylight on red

# Control top LED only
busylight on red --led 1

# Control bottom LED only  
busylight on blue --led 2

# Different colors on each LED
busylight on red --led 1
busylight on blue --led 2
```

**Platform Support:** macOS, Linux, Windows (experimental)

## Device Discovery

List connected devices to see what's available:

```bash
busylight list
```

Example output:
```
Connected Lights:
0: Blink(1) mk2
1: BlinkStick Square
2: Kuando Busylight Alpha
```

Use the index numbers to target specific devices:

```bash
busylight --lights 0 on red      # First device only
busylight --lights 1,2 on green  # Second and third devices
```

## Platform-Specific Setup

### Linux (udev rules required)

Generate and install udev rules for device access:

```bash
busylight udev-rules -o 99-busylights.rules
sudo cp 99-busylights.rules /etc/udev/rules.d/
sudo udevadm control -R
# Unplug and reconnect devices
```

### macOS

No additional setup required. System may prompt for USB device permissions.

### Windows (experimental)

Windows support is in development. Some devices may work, but full
compatibility is not guaranteed.

## Troubleshooting

### Device Not Found

1. **Check connections**: Verify USB cable and port
2. **List devices**: Run `busylight list` to see detected devices
3. **Linux**: Ensure udev rules are installed
4. **Permissions**: Check USB device permissions

### Device Appears But Won't Control

1. **Check device index**: Use `busylight list` to get correct index
2. **Try different colors**: Some devices have color limitations
3. **Check for conflicts**: Ensure no other software is controlling device
4. **Debug mode**: Run with `--debug` flag for detailed information

### Kuando Devices Stop Working

Kuando devices require active connection. If they stop responding:

1. Restart the busylight command
2. Ensure the process stays running (don't run in background)
3. Check USB connection stability

## Requesting New Device Support

To request support for additional devices, [open an issue][new-device] in
the Busylight Core project with:

- Device vendor and model
- USB vendor ID and product ID
- Device specifications and capabilities
- Sample device for testing (if possible)

[new-device]: https://github.com/JnyJny/busylight-core/issues/new?template=4_new_device_request.yaml
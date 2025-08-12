# BusyLight for Humans

BusyLight for Humans controls USB LED lights from multiple vendors. Use the
command-line interface or HTTP API to turn lights on/off, change colors, and
apply effects.

## Quick Start

### Installation

```bash
# Basic installation (CLI only)
pip install busylight-for-humans

# With web API support
pip install busylight-for-humans[webapi]
```

### Basic Usage

```bash
# Turn light on (green by default)
busylight on

# Turn light red
busylight on red

# Blink light blue 5 times
busylight blink blue --count 5

# Control specific LED on multi-LED devices
busylight on red --led 1
```

### Web API

```bash
# Start API server
busyserve

# Turn light on via HTTP
curl http://localhost:8000/light/0/on?color=red

# Blink light via HTTP
curl http://localhost:8000/light/0/blink?color=blue&count=3
```

## Features

- **Cross-platform**: macOS and Linux support (Windows in development)
- **Multiple interfaces**: Command-line and HTTP API
- **Device support**: 23 devices from 9 vendors
- **LED targeting**: Individual LED control for multi-LED devices
- **Effects**: Blinking, rainbow, pulse, and custom effects
- **Authentication**: Optional HTTP Basic Auth for API

## Supported Devices

| Vendor | Multi-LED Support |
|--------|------------------|
| Agile Innovative (BlinkStick) | ✓ |
| ThingM (Blink1 mk2) | ✓ |
| Luxafor (Flag variants) | ✓ |
| Kuando, Embrava, MuteMe | Single LED |

See the [devices overview](devices/index.md) for complete compatibility
information.

## Documentation Sections

- **[Installation](installation.md)**: Setup instructions for different
  platforms
- **[CLI](cli/index.md)**: Command-line interface reference and examples
- **[Web API](api/index.md)**: HTTP API endpoints and integration guide
- **[Devices](devices/index.md)**: Hardware compatibility and LED support

## Source Code

The project is open source and available on
[GitHub](https://github.com/JnyJny/busylight). For Python integration, see
[Busylight Core](https://github.com/JnyJny/busylight-core).
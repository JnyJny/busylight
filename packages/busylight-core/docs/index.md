# Busylight Core for Humans

A unified Python library for controlling USB status lights (busylights) from multiple vendors.

## Overview

Busylight Core provides a consistent interface to control various USB-connected status lights, commonly used for indicating availability, meeting status, or system notifications. The library abstracts away vendor-specific protocols and provides a clean, unified API for controlling lights from 9+ different manufacturers.

## Quick Start

Install busylight_core using pip:

```bash
pip install busylight_core
```

Then use it in your Python code:

```python
from busylight_core import Light, NoLightsFoundError

try:
    light = Light.first_light()
    light.on((255, 0, 0))  # Turn on red
    light.off()             # Turn off
except NoLightsFoundError:
    print("No compatible lights found")
```

## Features

- **Multi-Vendor Support** - Control devices from 9+ vendors (Embrava, Kuando, Luxafor, ThingM, and more)
- **Multiple Connection Types** - HID and Serial device support
- **Rich Light Control** - Colors, brightness, flash patterns
- **Audio Capabilities** - Sound playback on Embrava Blynclight Plus devices
- **Input Detection** - Button state on MuteMe and Luxafor Mute devices
- **Multi-LED Support** - Control devices with 1-64+ individual LEDs (BlinkStick, Luxafor Flag)
- **Async Task Management** - Built-in support for periodic tasks and animations
- **Extensible Architecture** - Easy to add support for new devices
- **Object-Oriented API** - Clean, intuitive programming interface

## Installation

For detailed installation instructions, see [Installation](getting-started/installation.md).

## Documentation

- [Getting Started](getting-started/quickstart.md) - Quick start guide
- [Features](user-guide/features.md) - Detailed feature documentation
- [API Reference](reference/index.md) - Complete API documentation
- [Contributing](contributing.md) - How to contribute to this project

## License

This project is licensed under the Apache-2.0 license.

## Support

- [GitHub Issues](https://github.com/JnyJny/busylight_core/issues)

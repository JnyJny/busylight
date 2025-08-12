<!-- agile-innovative blink(1) blinkstick bluetooth blynclight bt busylight busylight-alpha busylight-omega compulab embrava epos fit-statusb flag hid kuando luxafor mute muteme mutesync omega orb plantronics serial thingM usb --> 

![BusyLight Project Logo][LOGO]
<br>

[![Test & Publish][release-badge]][release]
![Version][pypi-version]
![Release Date][release-date]
![Python Version][python-version]
![License][license]
![Code Style: ruff][code-style]
![Monthly Downloads][monthly-downloads]
<br>

[BusyLight for Humans][busylight-for-humans] controls USB LED lights
from multiple vendors. Use the command-line interface or HTTP API to
turn lights on/off, change colors, and apply effects.

![All Supported Lights][DEMO]

## What is BusyLight?

BusyLight provides simple control over USB LED status lights to show your
availability, build status, system health, or any other visual indicator.
Perfect for home offices, development workflows, and team collaboration.

**Key Features:**
- **23 supported devices** from 9 vendors (Blink1, BlinkStick, Luxafor, etc.)
- **Command-line interface** with intuitive color and effect controls
- **HTTP API** with full documentation for automation and integration
- **Multi-LED targeting** for devices with multiple independent LEDs
- **Cross-platform** support for macOS and Linux (and maybe Windows, it's spotty).

## Supported Hardware

| **Vendor** | **Models** | **LED Support** |
|------------|------------|-----------------|
| **Agile Innovative** | BlinkStick, BlinkStick Pro, BlinkStick Square, BlinkStick Strip, BlinkStick Nano, BlinkStick Flex | Multi-LED targeting |
| **Compulab** | fit-statUSB | Single LED |
| **EPOS** | Busylight | Single LED |
| **Embrava** | Blynclight, Blynclight Mini, Blynclight Plus | Single LED |
| **Kuando** | Busylight Alpha, Busylight Omega | Single LED |
| **Luxafor** | Flag, Orb, Mute, Busy Tag, Bluetooth variants | Flag: Multi-LED, Others: Single LED |
| **MuteMe** | MuteMe Original, Mute Mini, MuteSync | Single LED |
| **Plantronics** | Status Indicator | Single LED |
| **ThingM** | Blink(1), Blink(1) mk2 | mk2: Multi-LED |

📖 **[Device setup guides →][docs-devices]**

## Installation

### Basic Install (CLI only)
```bash
# Using uvx (recommended)
uvx --from busylight-for-humans busylight list
```

```bash
# Using pip
pip install busylight-for-humans
```

### Web API Install
```bash
# Using uvx
uvx --from "busylight-for-humans[webapi]" busyserve
```

```bash
# Using pip
pip install busylight-for-humans[webapi]
```

### Linux Setup
Linux requires udev rules for USB device access:
```bash
busylight udev-rules -o 99-busylights.rules
sudo cp 99-busylights.rules /etc/udev/rules.d/
sudo udevadm control -R
# Unplug and reconnect your device
```

## Quick Start

### Command Line
```bash
# Basic usage
busylight on              # Green light
busylight on red          # Red light
busylight blink blue      # Blinking blue
busylight off             # Turn off

# Multi-LED devices (Blink1 mk2, BlinkStick, etc.)
busylight on red --led 1          # First LED only
busylight on blue --led 2         # Second LED only
busylight rainbow --led 1         # Rainbow on first LED
busylight pulse green --led 2     # Pulse on second LED
```

### Web API
```bash
# Start the server
busyserve

# Control via HTTP
curl "http://localhost:8000/light/0/on?color=red"
curl "http://localhost:8000/light/0/blink?color=blue&count=5"
curl "http://localhost:8000/lights/off"

# Multi-LED targeting
curl "http://localhost:8000/lights/on?color=red&led=1"
curl "http://localhost:8000/lights/rainbow?led=2"
```

## Documentation

📖 **[Complete Documentation →][docs]**

- **[Installation Guide][docs-installation]** - Detailed setup for all platforms
- **[CLI Reference][docs-cli]** - All commands, options, and examples
- **[Web API Guide][docs-api]** - REST endpoints and integration examples
- **[Device Support][docs-devices]** - Full compatibility matrix and LED targeting
- **[Integration Examples][docs-integration]** - CI/CD, monitoring, and automation

## Contributing

🛠️ **[Contributing Guide →][contributing]**

- Development environment setup
- Testing and code quality guidelines
- Architecture overview and design patterns
- Pull request process and coding standards

## Support

- **[Report Issues][issues]** - Bug reports and feature requests
- **[Request Device Support][device-request]** - New hardware support
- **[Discussions][discussions]** - Community help and questions

## Gratitude

Thank you to [@todbot][todbot] and [ThingM][thingm] for graciously gifting
`blink(1) mk3` lights to support this project!

<hr>

<!-- Links -->
[busylight-for-humans]: https://github.com/JnyJny/busylight
[busylight-core]: https://github.com/JnyJny/busylight-core
[docs]: https://jnyjny.github.io/busylight/
[docs-installation]: https://jnyjny.github.io/busylight/installation/
[docs-cli]: https://jnyjny.github.io/busylight/cli/
[docs-api]: https://jnyjny.github.io/busylight/api/
[docs-devices]: https://jnyjny.github.io/busylight/devices/
[docs-integration]: https://jnyjny.github.io/busylight/api/integration/
[contributing]: https://github.com/JnyJny/busylight/blob/master/CONTRIBUTING.md
[issues]: https://github.com/JnyJny/busylight/issues
[device-request]: https://github.com/JnyJny/busylight-core/issues/new?template=4_new_device_request.yaml
[discussions]: https://github.com/JnyJny/busylight/discussions
[uv-docs]: https://docs.astral.sh/uv/
[todbot]: https://github.com/todbot
[thingm]: https://thingm.com

<!-- Assets -->
[LOGO]: https://github.com/JnyJny/busylight/blob/master/assets/BusyLightForHumans.png
[DEMO]: https://github.com/JnyJny/busylight/blob/master/assets/HerdOfLights.png

<!-- Badges -->
[pypi-version]: https://img.shields.io/pypi/v/busylight-for-humans
[python-version]: https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FJnyJny%2Fbusylight%2Fmaster%2Fpyproject.toml
[license]: https://img.shields.io/pypi/l/busylight-for-humans
[code-style]: https://img.shields.io/badge/ruff-yellow?style=flat-square&label=Style&link=https%3A%2F%2Fastral.sh%2Fruff
[monthly-downloads]: https://img.shields.io/pypi/dm/busylight-for-humans
[release-date]: https://img.shields.io/github/release-date/JnyJny/busylight
[release-badge]: https://github.com/JnyJny/busylight/actions/workflows/release.yaml/badge.svg
[release]: https://github.com/JnyJny/busylight/actions/workflows/release.yaml

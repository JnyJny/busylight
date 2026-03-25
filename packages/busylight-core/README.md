
[![Release][badge-release]][release]
![Version][badge-pypi-version]
![Release Date][badge-release-date]
![Python Version][badge-python-version]
![License][badge-license]
![Monthly Downloads][badge-monthly-downloads]
# Busylight Core for Humans™

> A unified Python library for controlling USB status lights (busylights) from multiple vendors

**busylight-core** provides a consistent interface to control various
USB-connected status lights, commonly used for indicating
availability, meeting status, or system notifications. Were you
looking for a command-line interface to control your lights? Check out
[Busylight for Humans™][busylight-for-humans]!

## Features

- **Multi-Vendor Support** - Control devices from nine vendors.
- **Multiple Connection Types** - HID and Serial device support.
- **Python Library** - Clean, object-oriented API for easy integration.
- **Input Detection** - Button press handling on interactive devices.
- **Multi-LED Support** - Control devices with 1-192 individual LEDs.
- **Extensible Architecture** - Easy to add support for new devices.

## Supported Hardware

| Vendor | Device Models |
|--------|---------------|
| **Agile Innovative** | BlinkStick, BlinkStick Pro, BlinkStick Flex, BlickStick Nano, BlinkStick Strip, BlinkStick Square |
| **CompuLab** | fit-statUSB |
| **EPOS** | Busylight |
| **Embrava** | Blynclight, Blynclight Mini, Blynclight Plus, BLYNCUSB10, BLYNCUSB20 |
| **Kuando** | Busylight Alpha, Busylight Omega |
| **Luxafor** | Flag, Mute, Orb, Bluetooth |
| **MuteMe** | MuteMe, MuteMe Mini, MuteSync |
| **Plantronics** | Status Indicator |
| **ThingM** | Blink(1) |


## Installation

### Add to Your Project with uv
```console
uv add busylight_core
```

### Install with pip
```console
python3 -m pip install busylight_core
```

## Usage

**Basic usage (any compatible device):**
```python
from busylight_core import Light

lights = Light.all_lights()

print(f"Found {len(lights)} light(s)")

for light in lights:
    light.on((255, 0, 0))  # Turn on red
    light.off()            # Turn off
```

**Vendor-specific usage (recommended for production):**
```python
from busylight_core import EmbravaLights, LuxaforLights, KuandoLights

# Get all Embrava devices
embrava_lights = EmbravaLights.all_lights()
if embrava_lights:
    light = embrava_lights[0]
    light.on((255, 0, 0))  # Red

# Get all Luxafor devices
luxafor_lights = LuxaforLights.all_lights()
for light in luxafor_lights:
    light.on((0, 255, 0))  # Green

# Get first Kuando device
try:
    kuando_light = KuandoLights.first_light()
    kuando_light.on((0, 0, 255))  # Blue
except NoLightsFoundError:
    print("No Kuando devices found")
```

### Common Use Cases

**Meeting Status Indicator:**
```python
from busylight_core import Light

red = (255, 0, 0)
green = (0, 128, 0)
yellow = (255, 255, 0)

# Any device approach
light = Light.first_light()

# Available
light.on(green)

# In meeting  
light.on(red)

# Away
light.on(yellow)

light.off()
```
<!-- EJO Claude hallucinated this entire section.
**Enhanced Meeting Status with Audio (Embrava devices):**
```python
from busylight_core import EmbravaLights, NoLightsFoundError

try:
    light = EmbravaLights.first_light()
    
    # Available (quiet green)
    light.on((0, 255, 0))
    
    # In meeting (red with audio alert)
    light.on((255, 0, 0), sound=True)
    
    # Away (dim yellow)
    light.on((255, 255, 0))
    light.dim()
    
except NoLightsFoundError:
    print("No Embrava devices found")
```
-->

For detailed documentation including API reference, advanced usage examples, and device-specific information:

- **Full Documentation**: [https://JnyJny.github.io/busylight_core/][docs-busylight-core]
- **Installation Guide**: [Getting Started][docs-getting-started]
- **Quick Start Guide**: [Usage Guide][docs-quick-start]
- **API Reference**: [API Docs][docs-api-reference]

## Development

This project and it's virtual environment is managed using [uv][uv] and
is configured to support automatic activation of virtual environments
using [direnv][direnv]. Development activites such as linting and testing
are automated via [Poe The Poet][poe-the-poet], run `poe` after cloning
this repo for a list of tasks.

Check out [CONTRIBUTING.md][docs-contributing] for more development
details.

<hr>

[![gh:JnyJny/python-package-cookiecutter][python-package-cookiecutter-badge]][python-package-cookiecutter]

<!-- End Links -->
[busylight-for-humans]: https://github.com/JnyJny/busylight
[python-package-cookiecutter-badge]: https://img.shields.io/badge/Made_With_Cookiecutter-python--package--cookiecutter-green?style=for-the-badge
[python-package-cookiecutter]: https://github.com/JnyJny/python-package-cookiecutter
[badge-release]: https://github.com/JnyJny/busylight_core/actions/workflows/release.yaml/badge.svg
[release]: https://github.com/JnyJny/busylight_core/actions/workflows/release.yaml
[badge-pypi-version]: https://img.shields.io/pypi/v/busylight_core
[badge-release-date]: https://img.shields.io/github/release-date/JnyJny/busylight_core
[badge-python-version]: https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FJnyJny%2Fbusylight_core%2Fmain%2Fpyproject.toml
[badge-license]: https://img.shields.io/github/license/JnyJny/busylight_core
[badge-monthly-downloads]: https://img.shields.io/pypi/dm/busylight_core
[poe-the-poet]: https://poethepoet.natn.io
[uv]: https://docs.astral.sh/uv/
[direnv]: https://direnv.net
<!-- documentation links -->
[docs-busylight-core]: https://jnyjny.github.io/busylight-core/
[docs-getting-started]: https://jnyjny.github.io/busylight-core/getting-started/installation/
[docs-quick-start]: https://jnyjny.github.io/busylight-core/getting-started/installation/
[docs-feature-guide]: https://jnyjny.github.io/busylight-core/user-guide/features/
[docs-api-reference]: https://jnyjny.github.io/busylight-core/reference/
[docs-contributing]: https://github.com/JnyJny/busylight-core/blob/main/CONTRIBUTING.md


[![Release][badge-release]][release]
![Version][badge-pypi-version]
![Python Version][badge-python-version]
![License][badge-license]
![Monthly Downloads][badge-monthly-downloads]

# Busylight Core for Humans&#8482;

> A unified Python library for controlling USB status lights from
> multiple vendors.

**busylight-core** provides a consistent interface to control USB
LED status lights. If you want a command-line interface or HTTP
API, see [Busylight for Humans&#8482;][busylight-for-humans].

## Quick Start

```python
from busylight_core import Light

light = Light.first_light()
light.on((0, 128, 0))   # green
light.off()
```

## Installation

```console
uv add busylight_core
```

```console
pip install busylight_core
```

## Features

- **Multi-vendor support** -- 26 devices from 9 vendors
- **HID and serial** -- multiple connection types
- **Async effects** -- blink, pulse, rainbow, spectrum
- **Multi-LED targeting** -- devices with 1-192 individual LEDs
- **Input detection** -- button press handling on interactive devices
- **Extensible** -- plugin architecture for adding new devices

## Supported Hardware

| Vendor | Models |
|--------|--------|
| **Agile Innovative** | BlinkStick, BlinkStick Pro, Square, Strip, Nano, Flex |
| **CompuLab** | fit-statUSB |
| **EPOS** | Busylight |
| **Embrava** | Blynclight, Blynclight Mini, Blynclight Plus, BLYNCUSB10, BLYNCUSB20 |
| **Kuando** | Busylight Alpha, Busylight Omega |
| **Luxafor** | Flag, Orb, Mute, Bluetooth |
| **MuteMe** | MuteMe Original, MuteMe Mini, MuteSync |
| **Plantronics** | Status Indicator |
| **ThingM** | Blink(1), Blink(1) mk2 |

## Usage

**Find and control all connected lights:**
```python
from busylight_core import Light

for light in Light.all_lights():
    print(f"{light.name} by {light.vendor}")
    light.on((255, 0, 0))  # red
```

**Vendor-specific access:**
```python
from busylight_core import EmbravaLights, LuxaforLights

embrava = EmbravaLights.all_lights()
if embrava:
    embrava[0].on((255, 0, 0))

luxafor = LuxaforLights.all_lights()
for light in luxafor:
    light.on((0, 255, 0))
```

**Async effects:**
```python
import asyncio
from busylight_core import Light

light = Light.first_light()
asyncio.run(light.blink(color=(0, 0, 255), speed=1))
```

**Meeting status indicator:**
```python
from busylight_core import Light

light = Light.first_light()

light.on((0, 128, 0))    # available (green)
light.on((255, 0, 0))    # in meeting (red)
light.on((255, 255, 0))  # away (yellow)
light.off()
```

## Platform Support

- **macOS** -- works out of the box
- **Linux** -- requires udev rules for USB access
- **Windows** -- may work, untested, patches welcome

## Development

This project is part of a [uv workspace][uv-workspaces] monorepo.
Virtual environment activation is supported via [direnv][direnv].
Development tasks (linting, testing) are automated with
[Poe the Poet][poe-the-poet] -- run `poe` for a list of tasks.

See [CONTRIBUTING.md][contributing] for development details.

## License

[Apache License 2.0](https://github.com/JnyJny/busylight/blob/main/LICENSE)

<!-- Links (absolute URLs for PyPI rendering) -->
[busylight-for-humans]: https://pypi.org/project/busylight-for-humans/
[contributing]: https://github.com/JnyJny/busylight/blob/main/packages/busylight-core/CONTRIBUTING.md
[uv-workspaces]: https://docs.astral.sh/uv/concepts/workspaces/
[poe-the-poet]: https://poethepoet.natn.io
[direnv]: https://direnv.net

<!-- Badges (absolute URLs for PyPI rendering) -->
[badge-release]: https://github.com/JnyJny/busylight/actions/workflows/release-core.yaml/badge.svg
[release]: https://github.com/JnyJny/busylight/actions/workflows/release-core.yaml
[badge-pypi-version]: https://img.shields.io/pypi/v/busylight_core
[badge-python-version]: https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FJnyJny%2Fbusylight%2Fmain%2Fpackages%2Fbusylight-core%2Fpyproject.toml
[badge-license]: https://img.shields.io/pypi/l/busylight_core
[badge-monthly-downloads]: https://img.shields.io/pypi/dm/busylight_core

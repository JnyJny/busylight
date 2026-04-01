<!-- agile-innovative blink(1) blinkstick bluetooth blynclight busylight busylight-alpha busylight-omega compulab embrava epos fit-statusb flag hid kuando luxafor mute muteme mutesync omega orb plantronics serial thingM usb -->

![BusyLight Project Logo][LOGO]

<p align="center">
<strong>Control USB LED status lights from the command line and HTTP.</strong><br>
26 devices &middot; 9 vendors &middot; CLI &middot; HTTP API
</p>

<p align="center">

[![Test & Publish][release-badge]][release]
![Version][pypi-version]
![Python Version][python-version]
![License][license]
![Monthly Downloads][monthly-downloads]

</p>

[BusyLight for Humans&#8482;][busylight-for-humans] controls USB LED
lights from multiple vendors. Use the command-line interface or HTTP
API to turn lights on/off, change colors, and apply effects.

Built on [busylight-core][busylight-core], the Python library for USB
status light communication.

<img alt="All Supported Lights" src="https://raw.githubusercontent.com/JnyJny/busylight/main/packages/busylight/assets/HerdOfLights.png">
<p align="left">

Flag<sup>1</sup>,
Busylight Alpha<sup>2</sup>,
Blynclight Plus<sup>3</sup>,
Blink(1)<sup>4</sup>,
Mute<sup>5</sup>,
Blynclight<sup>6</sup>,
Orb<sup>7</sup>,
BusyLight Omega<sup>8</sup>,
BlinkStick Square<sup>9</sup>,
Blynclight Mini<sup>10</sup>,
MuteMe Original<sup>11</sup>,
fit-statUSB<sup>12</sup>,
MuteSync<sup>13</sup>,
Status Indicator<sup>14</sup>
</p>

## Quick Start

```bash
# Turn on a green light right now
uvx --from busylight-for-humans busylight on

# Red, blinking, then off
uvx --from busylight-for-humans busylight blink red
uvx --from busylight-for-humans busylight off
```

## Installation

```bash
# Basic install (CLI only)
pip install busylight-for-humans

# With web API support
pip install busylight-for-humans[webapi]
```

**Linux** requires udev rules for USB device access:
```bash
busylight udev-rules -o 99-busylights.rules
sudo cp 99-busylights.rules /etc/udev/rules.d/
sudo udevadm control -R
# Unplug and reconnect your device
```

## Supported Hardware

| Vendor | Models |
|--------|--------|
| **Agile Innovative** | BlinkStick, BlinkStick Pro, Square, Strip, Nano, Flex |
| **CompuLab** | fit-statUSB |
| **EPOS** | Busylight |
| **Embrava** | Blynclight, Blynclight Mini, Blynclight Plus, BLYNCUSB10, BLYNCUSB20 |
| **Kuando** | Busylight Alpha, Busylight Omega |
| **Luxafor** | Flag, Orb, Mute, Busy Tag, Bluetooth |
| **MuteMe** | MuteMe Original, MuteMe Mini, MuteSync |
| **Plantronics** | Status Indicator |
| **ThingM** | Blink(1), Blink(1) mk2 |

Multi-LED targeting supported on BlinkStick variants, Luxafor Flag,
and Blink(1) mk2.

## Command Line

```bash
busylight on              # green light
busylight on red          # red light
busylight blink blue      # blinking blue
busylight rainbow         # cycle through colors
busylight off             # turn off

# Multi-LED devices
busylight on red --led 1  # first LED only
busylight on blue --led 2 # second LED only
```

## Web API

```bash
# Start the server
busyserve

# Control via HTTP
curl "http://localhost:8000/light/0/on?color=red"
curl "http://localhost:8000/light/0/blink?color=blue&count=5"
curl "http://localhost:8000/lights/off"
```

## Platform Support

- **macOS** -- works out of the box
- **Linux** -- requires udev rules (see Installation)
- **Windows** -- may work, untested, patches welcome

## Contributing

Contributions welcome. See [CONTRIBUTING.md][contributing] for
development setup and guidelines. This project is part of a
[uv workspace][uv-workspaces] monorepo.

## Gratitude

Thank you to [@todbot][todbot] and [ThingM][thingm] for gifting
`blink(1) mk3` lights to support this project.

## License

[Apache License 2.0](https://github.com/JnyJny/busylight/blob/main/LICENSE)

<!-- Links -->
[busylight-for-humans]: https://github.com/JnyJny/busylight/tree/main/packages/busylight
[busylight-core]: https://pypi.org/project/busylight-core/
[contributing]: https://github.com/JnyJny/busylight/blob/main/packages/busylight/CONTRIBUTING.md
[uv-workspaces]: https://docs.astral.sh/uv/concepts/workspaces/
[todbot]: https://github.com/todbot
[thingm]: https://thingm.com

<!-- Assets (absolute URLs for PyPI rendering) -->
[LOGO]: https://raw.githubusercontent.com/JnyJny/busylight/main/packages/busylight/assets/BusyLightForHumans.png
[DEMO]: https://raw.githubusercontent.com/JnyJny/busylight/main/packages/busylight/assets/HerdOfLights.png

<!-- Badges -->
[pypi-version]: https://img.shields.io/pypi/v/busylight-for-humans
[python-version]: https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FJnyJny%2Fbusylight%2Fmain%2Fpackages%2Fbusylight%2Fpyproject.toml
[license]: https://img.shields.io/pypi/l/busylight-for-humans
[monthly-downloads]: https://img.shields.io/pypi/dm/busylight-for-humans
[release-badge]: https://github.com/JnyJny/busylight/actions/workflows/release-cli.yaml/badge.svg
[release]: https://github.com/JnyJny/busylight/actions/workflows/release-cli.yaml

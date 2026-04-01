<!-- agile-innovative blink(1) blinkstick bluetooth blynclight busylight busylight-alpha busylight-omega compulab embrava epos fit-statusb flag hid kuando luxafor mute muteme mutesync omega orb plantronics serial thingM usb python usb-led status-light busy-light availability-indicator home-office work-from-home -->

![BusyLight Project Logo][LOGO]

<p align="center">
<strong>Control USB LED status lights from Python.</strong><br>
26 devices &middot; 9 vendors &middot; CLI &middot; HTTP API &middot; Python library
</p>

<p align="center">
<img alt="License" src="https://img.shields.io/pypi/l/busylight-for-humans">
<img alt="Python version" src="https://img.shields.io/pypi/pyversions/busylight-for-humans">
</p>

![All Supported Lights][DEMO]
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

```python
# Or from Python
from busylight_core import Light

light = Light.first_light()
light.on((0, 128, 0))   # green
light.off()
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

Multi-LED targeting supported on BlinkStick variants, Luxafor Flag, and Blink(1) mk2.

## Packages

This repository contains two packages that work together:

### [Busylight for Humans&#8482;][busylight-cli]  &mdash; CLI & Web API

![PyPI version](https://img.shields.io/pypi/v/busylight-for-humans)
![Monthly downloads](https://img.shields.io/pypi/dm/busylight-for-humans)

The user-facing tools. Install this if you want to control lights from
the command line or expose an HTTP API for automation.

```bash
pip install busylight-for-humans
```

**Command line:**
```bash
busylight on red          # solid red
busylight blink blue      # blinking blue
busylight rainbow         # cycle through colors
busylight on green --led 1  # target specific LED
busylight off             # turn off
```

**Web API:**
```bash
pip install busylight-for-humans[webapi]
busyserve  # starts on http://localhost:8000

curl "http://localhost:8000/light/0/on?color=red"
curl "http://localhost:8000/lights/off"
```

[Full documentation][busylight-cli-docs]

### [Busylight Core for Humans&#8482;][busylight-core] &mdash; Python Library

![PyPI version](https://img.shields.io/pypi/v/busylight-core)
![Monthly downloads](https://img.shields.io/pypi/dm/busylight-core)

The device communication layer you can use if you're building your own
tools or integrating status lights into a larger system.

```bash
uv add busylight_core
```

```python
from busylight_core import Light

# Find and control lights
for light in Light.all_lights():
    print(f"{light.name} by {light.vendor}")
    light.on((255, 0, 0))  # red

# Async effects
import asyncio
light = Light.first_light()
asyncio.run(light.blink(color=(0, 0, 255), speed=1))
```

Features: multi-vendor abstraction, HID and serial support, async
effects, button/input detection, multi-LED targeting, plugin
architecture for adding new devices.

[Full documentation][busylight-core-docs]

## Platform Support

- **macOS** &mdash; works out of the box
- **Linux** &mdash; requires udev rules for USB access:
  ```bash
  busylight udev-rules -o 99-busylights.rules
  sudo cp 99-busylights.rules /etc/udev/rules.d/
  sudo udevadm control -R
  ```
- **Windows** &mdash; may work, untested, patches welcome

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for
development setup, workflow, and guidelines. This is a
[uv workspace][uv-workspaces] &mdash; one clone, one venv, both
packages.

## Gratitude

Thank you to [@todbot][todbot] and [ThingM][thingm] for gifting
`blink(1) mk3` lights to support this project.

## License

Both packages are licensed under the [Apache License 2.0](LICENSE).

<!-- Links -->
[busylight-cli]: packages/busylight/
[busylight-core]: packages/busylight-core/
[busylight-cli-docs]: https://jnyjny.github.io/busylight/
[busylight-core-docs]: https://github.com/JnyJny/busylight/tree/main/packages/busylight-core#readme

[uv-workspaces]: https://docs.astral.sh/uv/concepts/workspaces/
[todbot]: https://github.com/todbot
[thingm]: https://thingm.com

<!-- Assets -->
[LOGO]: packages/busylight/assets/BusyLightForHumans.png
[DEMO]: packages/busylight/assets/HerdOfLights.png

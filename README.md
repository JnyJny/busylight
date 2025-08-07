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

[BusyLight for Humans™][busylight-for-humans] gives you control of USB
attached LED lights from a variety of vendors. Lights can be
controlled via the command-line or using a HTTP API. Please consider
[Busylight Core][busylight-core] if you'd like to integrate USB light
control into your own Python application.

![All Supported Lights][DEMO]
Flag<sup>1</sup>,
Busylight Alpha<sup>2</sup>,
Status Indicator<sup>3</sup>,
Blink(1)<sup>4</sup>,
Mute<sup>5</sup>,
Blynclight<sup>6</sup>.
Orb<sup>7</sup>,
BusyLight Omega<sup>8</sup>,
BlinkStick Square<sup>9</sup>,
Blynclight Mini<sup>10</sup>,
MuteMe Original<sup>11</sup>,
fit-statUSB<sup>12</sup>,
MuteSync<sup>13</sup>, 
Blynclight Plus<sup>14</sup>

## Features
- Control lights from the command-line.
- Control lights via HTTP API.
- Supported on MacOS and Linux
- Windows support is in progress.
- Support for twenty-three devices from nine vendors:

| **Vendor** |  **Models** |
|------------|-------------|
| [**Agile Innovative**][2] | BlinkStick, BlinkStick Pro, BlinkStick Square, BlinkStick Strip, BlinkStick Nano, BlickStick Flex |
| [**Compulab**][8] | fit-statUSB |
| [**EPOS**][11] | Busylight |
| [**Embrava**][3] | Blynclight, Blynclight Mini, Blynclight Plus |
| [**Kuando**][4] | Busylight Alpha, BusyLight Omega |
| [**Luxafor**][5] | Bluetooth, Flag, Mute, Orb, Busy Tag |
| [**Plantronics**][3] | Status Indicator |
| [**MuteMe**][7] | MuteMe Original, Mute Mini, MuteSync |
| [**ThingM**][6] | Blink(1) |

Request support for a new device by [opening an issue][busylight-core-issues]
in the Busylight Core project.

## Basic Install

Installs only the command-line `busylight` tool and associated
modules.

### **uvx**
```console
uvx --from busylight-for-humans busylight list
```

### **pip**
```console
python3 -m pip install busylight-for-humans 
```

## Web API Install

Installs `uvicorn` and `FastAPI` in addition to `busylight`:

### **uvx**
```console
uvx --from "busylight-for-humans[webapi]" busyserve
```

### **pip**
```console
python3 -m pip install busylight-for-humans[webapi]
```

## Development Install

This project is managed using [uv][uv-docs] for:
- dependency management
- pytest configuration
- versioning
- optional dependencies
- virtual environment creation
- building packages
- publishing packages to PyPi via GitHub Actions


```console
$ python3 -m pip install uv
$ cd path/to/busylight
$ uv sync --all-extras
$ source .venv/bin/activate
<venv> $ which busylight
<venv> $ which busyserve
<venv> $ pytest
```

After installing into the virtual environment, the project is now
available in editable mode.  Changes made in the source will be
reflected in the runtime behavior when running in the uv managed
virtual environment.

## Linux Post-Install Activities

Linux controls access to USB devices via the [udev subsystem][UDEV]. By
default it denies non-root users access to devices it doesn't
recognize. I've got you covered!

You'll need root access to configure the udev rules:

```console
$ busylight udev-rules -o 99-busylights.rules
$ sudo cp 99-busylights.rules /etc/udev/rules.d
$ sudo udevadm control -R
$ # unplug/plug your light
$ busylight on
```

## Command-Line Examples

```console
$ busylight on               # light turns on green
$ busylight on red           # now it's shining a friendly red
$ busylight on 0xff0000      # still red
$ busylight on #0000ff       # now it's blue!
$ busylight blink            # it's slowly blinking on and off with a red color
$ busylight blink green fast # blinking faster green and off
$ busylight --all on         # turn all lights on green
$ busylight --all off        # turn all lights off
```

## HTTP API Examples

First start the `busylight` API server using the `busyserv` command line interface:
```console
$ busyserve -D
INFO:     Started server process [40064]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
...
```

The API is fully documented and available via these URLs:

- `https://localhost:8000/redoc`
- `https://localhost:8000/docs`


Now you can use the web API endpoints which return JSON payloads:

```console
  $ curl -s http://localhost:8000/lights/status | jq
  ...
  
  $ curl -s http://localhost:8000/light/0/status | jq
  ...
  
  $ curl -s http://localhost:8000/light/0/on | jq
  {
    "light_id": 0,
    "action": "on",
    "color": "green",
    "rgb": [0, 128, 0]
  }
  
  $ curl -s http://localhost:8000/light/0/off | jq
  {
    "light_id": 0,
    "action": "off"
  }
  
  $ curl -s http://localhost:8000/light/0/on?color=purple | jq
  {
    "light_id": 0,
    "action": "on",
    "color": "purple",
    "rgb": [128, 0, 128]
  }
  
  $ curl -s http://localhost:8000/lights/on | jq
  {
    "light_id": "all",
    "action": "on",
    "color": "green",
    "rgb", [0, 128, 0]
  }
  
  $ curl -s http://localhost:8000/lights/off | jq
  {
    "light_id": "all",
    "action": "off"
  }
  
  $ curl -s http://localhost:8000/lights/rainbow | jq
  {
    "light_id": "all",
    "action": "effect",
    "name": "rainbow"
  }
```

### Authentication
The API can be secured with a simple username and password through
[HTTP Basic Authentication][BASICAUTH]. To require authentication
for all API requests, set the `BUSYLIGHT_API_USER` and
`BUSYLIGHT_API_PASS` environmental variables before running
`busyserve`.

> :warning: **SECURITY WARNING**: HTTP Basic Auth sends usernames and passwords in *cleartext* (i.e., unencrypted). Use of SSL is highly recommended!

### Gratitude

Thank you to [@todbot][todbot] and the very nice people at [ThingM][thingm] who
graciously and unexpectedly gifted me with two `blink(1) mk3` lights!

<hr>

<!-- End Links -->
[busylight-for-humans]: https://github.com/JnyJny/busylight
[busylight-core]: https://github.com/JnyJny/busylight-core
[busylight-core-issues]: https://github.com/JnyJny/busylight-core/issues/new?template=4_new_device_request.yaml

<!-- Doc links -->
[2]: https://github.com/JnyJny/busylight/blob/master/docs/devices/agile_innovative.md
[3]: https://github.com/JnyJny/busylight/blob/master/docs/devices/embrava.md
[4]: https://github.com/JnyJny/busylight/blob/master/docs/devices/kuando.md
[5]: https://github.com/JnyJny/busylight/blob/master/docs/devices/luxafor.md
[6]: https://github.com/JnyJny/busylight/blob/master/docs/devices/thingm.md
[7]: https://github.com/JnyJny/busylight/blob/master/docs/devices/muteme.md
[8]: https://github.com/JnyJny/busylight/blob/master/docs/devices/compulab.md
[9]: https://github.com/JnyJny/busylight/blob/master/docs/devices/mutesync.md
[10]: https://github.com/JnyJny/busylight/blob/master/docs/devices/busytag.md
[11]: https://github.com/JnyJny/busylight/blob/master/docs/devices/epos.md

<!-- Asset links -->

[LOGO]: https://github.com/JnyJny/busylight/blob/master/docs/assets/BusyLightForHumans.png
[DEMO]: https://github.com/JnyJny/busylight/blob/master/docs/assets/HerdOfLights.png

<!-- Miscellaneous -->
[BASICAUTH]: https://en.wikipedia.org/wiki/Basic_access_authentication
[UDEV]: https://en.wikipedia.org/wiki/Udev
[uv-docs]: https://docs.astral.sh/uv/
[todbot]: https://github.com/todbot
[thingm]: https://thingm.com

<!-- badges -->

[pypi-version]: https://img.shields.io/pypi/v/busylight-for-humans
[python-version]: https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FJnyJny%2Fbusylight%2Fmaster%2Fpyproject.toml
[license]: https://img.shields.io/pypi/l/busylight-for-humans
[code-style]: https://img.shields.io/badge/ruff-yellow?style=flat-square&label=Style&link=https%3A%2F%2Fastral.sh%2Fruff

[dependencies]: https://img.shields.io/librariesio/github/JnyJny/busylight
[monthly-downloads]: https://img.shields.io/pypi/dm/busylight-for-humans
[release-date]: https://img.shields.io/github/release-date/JnyJny/busylight
[release-badge]: https://github.com/JnyJny/busylight/actions/workflows/release.yaml/badge.svg
[release]: https://github.com/JnyJny/busylight/actions/workflows/release.yaml

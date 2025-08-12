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

[BusyLight for Humans][busylight-for-humans] controls USB LED lights from
multiple vendors. Use the command-line interface or HTTP API to turn lights
on/off, change colors, and apply effects. For Python integration, use
[Busylight Core][busylight-core] directly in your applications.

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
- Command-line interface with color, effect, and LED targeting options
- HTTP API with full documentation and authentication support  
- Individual LED control for multi-LED devices (Blink1 mk2, BlinkStick variants)
- Cross-platform support: macOS and Linux (Windows in development)
- Support for 23 devices from 9 vendors:

| **Vendor** |  **Models** | **LED Support** |
|------------|-------------|-----------------|
| [**Agile Innovative**][2] | BlinkStick, BlinkStick Pro, BlinkStick Square, BlinkStick Strip, BlinkStick Nano, BlinkStick Flex | Multi-LED targeting |
| [**Compulab**][8] | fit-statUSB | Single LED |
| [**EPOS**][11] | Busylight | Single LED |
| [**Embrava**][3] | Blynclight, Blynclight Mini, Blynclight Plus | Single LED |
| [**Kuando**][4] | Busylight Alpha, BusyLight Omega | Single LED |
| [**Luxafor**][5] | Bluetooth, Flag, Mute, Orb, Busy Tag | Single LED |
| [**Plantronics**][3] | Status Indicator | Single LED |
| [**MuteMe**][7] | MuteMe Original, Mute Mini, MuteSync | Single LED |
| [**ThingM**][6] | Blink(1), Blink(1) mk2 | Blink(1) mk2: Multi-LED |

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

This project uses [uv][uv-docs] for dependency management, virtual
environments, and packaging.

```console
$ python3 -m pip install uv
$ cd path/to/busylight
$ uv sync --all-extras
$ source .venv/bin/activate
<venv> $ which busylight
<venv> $ which busyserve
<venv> $ pytest
```

The project installs in editable mode. Source changes are reflected
immediately when running in the virtual environment.

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

### Basic Usage
```console
$ busylight on               # light turns on green
$ busylight on red           # turns red
$ busylight on 0xff0000      # red using hex
$ busylight on #0000ff       # blue using hex
$ busylight blink            # slow red blinking
$ busylight blink green fast # fast green blinking
$ busylight --all on         # turn all lights on green
$ busylight --all off        # turn all lights off
```

### LED Targeting (Multi-LED Devices)
```console
$ busylight on red --led 1          # turn on top LED only (Blink1 mk2)
$ busylight on blue --led 2         # turn on bottom LED only  
$ busylight blink green --led 1 --count 5  # blink top LED 5 times
$ busylight off                     # turn off all LEDs (default)
```

## HTTP API Examples

First start the `busylight` API server using the `busyserv` command line
interface:
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

### Basic Operations
```console
$ curl -s http://localhost:8000/lights/status | jq
# Returns status of all lights

$ curl -s http://localhost:8000/light/0/on | jq
{
  "light_id": 0,
  "action": "on", 
  "color": "green",
  "rgb": [0, 128, 0],
  "led": 0
}

$ curl -s http://localhost:8000/light/0/on?color=purple | jq
{
  "light_id": 0,
  "action": "on",
  "color": "purple", 
  "rgb": [128, 0, 128],
  "led": 0
}

$ curl -s http://localhost:8000/light/0/blink?color=red&count=3 | jq
{
  "light_id": 0,
  "action": "blink",
  "color": "red",
  "rgb": [255, 0, 0],
  "count": 3,
  "led": 0
}
```

### LED Targeting (Multi-LED Devices)
```console
$ curl -s "http://localhost:8000/light/0/on?color=red&led=1" | jq
{
  "light_id": 0,
  "action": "on",
  "color": "red",
  "rgb": [255, 0, 0],
  "led": 1
}

$ curl -s "http://localhost:8000/light/0/blink?color=blue&led=2&count=5" | jq
{
  "light_id": 0,
  "action": "blink", 
  "color": "blue",
  "rgb": [0, 0, 255],
  "count": 5,
  "led": 2
}
```

## LED Parameter Reference

For devices with multiple LEDs (like Blink1 mk2), use the `--led` option
(CLI) or `led` parameter (API):

- `led=0`: Control all LEDs (default behavior)
- `led=1`: Control first/top LED  
- `led=2`: Control second/bottom LED
- `led=3+`: Control additional LEDs (BlinkStick variants)

Single-LED devices ignore the LED parameter. Device-specific LED indexing
varies by manufacturer.

### Authentication
The API can be secured with a simple username and password through
[HTTP Basic Authentication][BASICAUTH]. To require authentication
for all API requests, set the `BUSYLIGHT_API_USER` and
`BUSYLIGHT_API_PASS` environmental variables before running
`busyserve`.

> :warning: **SECURITY WARNING**: HTTP Basic Auth sends usernames and
> passwords in *cleartext* (i.e., unencrypted). Use of SSL is highly
> recommended!

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

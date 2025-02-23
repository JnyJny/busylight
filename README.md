<!-- USB HID API embrava blynclight agile innovative blinkstick kuando busylight omega alpha plantronics luxafor bluetooth bt flag mute orb thingM blink(1) muteme mutesync compulab fit-statusb -->
![BusyLight Project Logo][LOGO]
<br>
![version][pypi-version]
![monthly-downloads][monthly-downloads]
![visits][visits]
![supported python versions][python-versions] 
![license][license]
![Code style: black][code-style-black]
<br>
[![pytest-linux](https://github.com/JnyJny/busylight/actions/workflows/pytest-linux.yaml/badge.svg)](https://github.com/JnyJny/busylight/actions/workflows/pytest-linux.yaml)
[![MacOS](https://github.com/JnyJny/busylight/actions/workflows/pytest-macos.yaml/badge.svg)](https://github.com/JnyJny/busylight/actions/workflows/pytest-macos.yaml)
[![pytest-windows](https://github.com/JnyJny/busylight/actions/workflows/pytest-windows.yaml/badge.svg)](https://github.com/JnyJny/busylight/actions/workflows/pytest-windows.yaml)
<br>

[BusyLight for Humans™][0] gives you control of USB attached LED
lights from a variety of vendors. Lights can be controlled via
the command-line, using a HTTP API or imported directly into your own
Python project.

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
- Control lights from the [command-line][HELP].
- Control lights via a [Web API][WEBAPI].
- Import `busylight` into your own Python project.
- Supported on MacOS and Linux
- Windows support is untested but there are reports that it is working.
- Supports _ten_ vendors & seventeen devices:

| **Vendor** | | | | |
|------------:|---|---|---|---|
| [**Agile Innovative**][2] | BlinkStick Square |
| [**Busy Tag**][10] | Busy Tag |
| [**Compulab**][8] | fit-statUSB |
| [**Embrava**][3] | Blynclight | Blynclight Mini | Blynclight Plus |
| [**Kuando**][4] | Busylight Alpha | BusyLight Omega |
| [**Luxafor**][5] | Bluetooth | Flag | Mute | Orb |
| [**Plantronics**][3] | Status Indicator |
| [**MuteMe**][7] | MuteMe Original | Mute Mini |
| [**MuteSync**][9] | MuteSync |
| [**ThingM**][6] | Blink(1) |

If you have a USB light that's not on this list open an issue with:
 - the make and model device you want supported
 - where I can get one
 - any public hardware documentation you are aware of
 
Or even better, open a pull request!

### Gratitude

Thank you to [@todbot][todbot] and the very nice people at [ThingM][thingm] who
graciously and unexpectedly gifted me with two `blink(1) mk3` lights!

## Basic Install

Installs only the command-line `busylight` tool and associated
modules.

```console
$ python3 -m pip install busylight-for-humans 
```

## Web API Install

Installs `uvicorn` and `FastAPI` in addition to `busylight`:

```console
$ python3 -m pip install busylight-for-humans[webapi]
```

## Development Install

I use the tool [poetry][poetry-docs] to manage various aspects of this project, including:
- dependencies
- pytest configuration
- versioning
- optional dependencies
- virtual environment creation
- building packages
- publishing packages to PyPi

```console
$ python3 -m pip install poetry 
$ cd path/to/busylight
$ poetry shell
<venv> $ poetry install -E webapi
<venv> $ which busylight
<venv> $ which busyserve
```

After installing into the virtual environment, the project is now available in editable mode.  Changes made in the source will be reflected in the runtime behavior when running in the poetry initiated shell.

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
$ busylight on #00ff00       # now it's blue!
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

## Code Examples

Adding light support to your own python applications is easy!

### Simple Case: Turn On a Single Light

In this example, we pick an Embrava Blynclight to activate with
the color white. Colors are specified as a three-tuple of integers
that range from 0 to 255 and represent red, green, and blue
in that order.

```python
from busylight.lights.embrava import Blynclight

light = Blynclight.first_light()

light.on((255, 255, 255))

light.off()
```

Not sure what light you've got? No problem!

```python
from busylight.lights import Light

light = Light.first_light()

light.on((0xff, 0, 0xff))

light.off()
```

### Slightly More Complicated

The `busylight` package includes a manager class that's great for
working with multiple lights or lights that require a little
more direct intervention like the Kuando Busylight family.

```python
from busylight.manager import LightManager
from busylight.effects import Effects

manager = LightManager()
for light in manager.lights:
   print(light.name)
   
rainbow = Effects.for_name("spectrum")(duty_cycle=0.05)

manager.apply_effect(rainbow)
...
manager.off()
```

[0]: https://github.com/JnyJny/busylight


<!-- doc links -->
[2]: https://github.com/JnyJny/busylight/blob/master/docs/devices/agile_innovative.md
[3]: https://github.com/JnyJny/busylight/blob/master/docs/devices/embrava.md
[4]: https://github.com/JnyJny/busylight/blob/master/docs/devices/kuando.md
[5]: https://github.com/JnyJny/busylight/blob/master/docs/devices/luxafor.md
[6]: https://github.com/JnyJny/busylight/blob/master/docs/devices/thingm.md
[7]: https://github.com/JnyJny/busylight/blob/master/docs/devices/muteme.md
[8]: https://github.com/JnyJny/busylight/blob/master/docs/devices/compulab.md
[9]: https://github.com/JnyJny/busylight/blob/master/docs/devices/mutesync.md
[10]: https://github.com/JnyJny/busylight/blob/master/docs/devices/busytag.md

[LOGO]: https://github.com/JnyJny/busylight/blob/master/docs/assets/BusyLightForHumans.png
[HELP]: https://github.com/JnyJny/busylight/blob/master/docs/busylight.1.md
[WEBAPI]: https://github.com/JnyJny/busylight/blob/master/docs/busylight_api.pdf

<!-- [DEMO]: demo/demo-updated.gif -->
[DEMO]: https://github.com/JnyJny/busylight/blob/master/docs/assets/HerdOfLights.png

[BASICAUTH]: https://en.wikipedia.org/wiki/Basic_access_authentication
[UDEV]: https://en.wikipedia.org/wiki/Udev

[todbot]: https://github.com/todbot
[thingm]: https://thingm.com

<!-- badges -->

[code-style-black]: https://img.shields.io/badge/code%20style-black-000000.svg
[pypi-version]: https://img.shields.io/pypi/v/busylight-for-humans
[python-versions]: https://img.shields.io/pypi/pyversions/busylight-for-humans
[license]: https://img.shields.io/pypi/l/busylight-for-humans
[dependencies]: https://img.shields.io/librariesio/github/JnyJny/busylight
[monthly-downloads]: https://img.shields.io/pypi/dm/busylight-for-humans
[poetry-docs]: https://python-poetry.org/docs/
[visits]: https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FJnyJny%2Fbusylight&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=Visits&edge_flat=false

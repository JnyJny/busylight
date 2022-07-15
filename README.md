<!-- USB HID API embrava blynclight agile innovative blinkstick kuando busylight omega alpha plantronics luxafor flag mute orb thingM blink(1) muteme -->
![version][pypi-version]
![monthly-downloads][monthly-downloads]
![supported python versions][python-versions] 
![license][license]
![Code style: black][code-style-black]
<br>
[![pytest-linux](https://github.com/JnyJny/busylight/actions/workflows/pytest-linux.yaml/badge.svg)](https://github.com/JnyJny/busylight/actions/workflows/pytest-linux.yaml)
[![MacOS](https://github.com/JnyJny/busylight/actions/workflows/pytest-macos.yaml/badge.svg)](https://github.com/JnyJny/busylight/actions/workflows/pytest-macos.yaml)
[![pytest-windows](https://github.com/JnyJny/busylight/actions/workflows/pytest-windows.yaml/badge.svg)](https://github.com/JnyJny/busylight/actions/workflows/pytest-windows.yaml)
<br>

![BusyLight Project Logo][LOGO]


[BusyLight for Humans™][0] gives you control of USB attached LED
lights from a variety of vendors. Lights can be controlled via
the command-line, using a HTTP API or imported directly into your own
Python project.

![All Supported Lights][DEMO]

**Eight Lights Attached to One Host**<br>
<em>Back to Front, Left to Right</em> <br>
<b>Busylight Alpha, Plantronics Status Indicator, BlyncLight, BlyncLight Plus</b><br>
<b>BlinkStick, Busylight Omega, Blink(1), Flag</b>

## Features
- Control lights from the [command-line][HELP].
- Control lights via a [Web API][WEBAPI].
- Import `busylight` into your own Python project.
- Supports _seven_ vendors & multiple models:
 
| [**Agile Innovative**][2] | [**Embrava**][3] |  [**MuteMe**][7] | [**Plantronics**][3]| [**Kuando**][4]| [**Luxafor**][5] | [**ThingM**][6] |
|-----------------------|------------------|-------------------|--------------|----------------|---------------|---------------|
| BlinkStick		    | Blynclight       | MuteMe Original (prototype) | Status Indicator    | Busylight Alpha|  Flag            | Blink(1)        |
| BlinkStick Pro	    | Blynclight Mini  | MuteMe Original (production) |	             | Busylight Omega|  Mute            | 
| BlinkStick Square	    | Blynclight Plus  | Mute Mini |                    |                |  Orb             |                 | 
| BlinkStick Strip      |
| BlinkStick Nano	    |
| BlinkStick Flex       |

- Supported on MacOS and Linux
- Windows support will be available in the near future.

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
INFO:     Started server process [20189]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

The API is fully documented and available @ `https://localhost:8888/redoc`


Now you can use the web API endpoints which return JSON payloads:

```console
  $ curl -s http://localhost:8888/lights/status | jq
  ...
  $ curl -s http://localhost:8888/light/0/status | jq
  ...
  $ curl -s http://localhost:8888/light/0/on | jq
  {
    "light_id": 0,
    "action": "on",
    "color": "green",
	"rgb": [0, 128, 0]
  }
  $ curl -s http://localhost:8888/light/0/off | jq
  {
    "light_id": 0,
    "action": "off"
  }
  $ curl -s http://localhost:8888/light/0/on?color=purple | jq
  {
    "light_id": 0,
    "action": "on",
    "color": "purple",
	"rgb": [128, 0, 128]
  }
  $ curl -s http://localhost:8888/lights/on | jq
  {
    "light_id": "all",
    "action": "on",
    "color": "green",
	"rgb", [0, 128, 0]
  }
  $ curl -s http://localhost:8888/lights/off | jq
  {
    "light_id": "all",
    "action": "off"
  }
  $ curl -s http://localhost:8888/lights/rainbow | jq
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
the color white. 

```python
from busylight.lights.embrava import Blynclight

light = Blynclight.first_light()

light.on((255, 255, 255))
```

Not sure what light you've got? 

```python
from busylight.lights import USBLight

light = USBLight.first_light()

light.on((0xff, 0, 0xff))
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
[2]: docs/devices/agile_innovative.md
[3]: docs/devices/embrava.md
[4]: docs/devices/kuando.md
[5]: docs/devices/luxafor.md
[6]: docs/devices/thingm.md
[7]: docs/devices/muteme.md

[LOGO]: docs/assets/BusyLightLogo.png
[HELP]: docs/busylight.1.md
[WEBAPI]: docs/busylight_api.pdf
[DEMO]: demo/demo-updated.gif

[BASICAUTH]: https://en.wikipedia.org/wiki/Basic_access_authentication
[UDEV]: https://en.wikipedia.org/wiki/Udev

[todbot]: https://github.com/todbot
[thingm]: https://thingm.com

<!-- badges -->
[pytest-badge]: actions/workflows/pytest.yaml/badge.svg
[pytest-status]: actions/workflows/pytest.yaml
[code-style-black]: https://img.shields.io/badge/code%20style-black-000000.svg
[pypi-version]: https://img.shields.io/pypi/v/busylight-for-humans
[python-versions]: https://img.shields.io/pypi/pyversions/busylight-for-humans
[license]: https://img.shields.io/pypi/l/busylight-for-humans
[dependencies]: https://img.shields.io/librariesio/github/JnyJny/busylight
[monthly-downloads]: https://img.shields.io/pypi/dm/busylight-for-humans


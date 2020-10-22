# `busylight`

Control USB attached LED lights like a Human™

![All supported lights](https://github.com/JnyJny/busylight/raw/master/demo/demo.gif)

Make a USB attached LED light turn on, off and blink; all from the
comfort of your very own command-line. If your platform supports
HIDAPI (Linux, MacOS, Windows and probably others), then you can use
`busylight` with supported lights!

## Usage


```console
$ busylight on
$ busylight off
$ busylight on purple
$ busylight on 0xff00ff   # still purple.
$ busylight blink yellow  # all hands man your stations.
$ busylight blink red     # RED ALERT!
$ busylight off           # all clear.
```

## Supported Lights


```console
$ busylight supported
Agile Innovations BlinkStick (†)
Embrava Blynclight
ThingM Blink1
Kuando BusyLight (‡)
Luxafor Flag
```

 
- † Requires software intervention for `blink` mode
- ‡ Requires software intervention for all modes

Lights that "require software intervention" need software to constantly update
the device instead of a one-time configuration of the light. Those devices will
cause the `busylight` command to not return immediately and the lights will
turn off when the user interrupts the command. The `busylight serve` mode can
help in this situation.

## Install


```console
$ pip install -U busylight-for-humans
$ busylight --help
```

### Install with web API support using FastAPI & Uvicorn


```console
$ pip install -U busylight-for-humans[webapi]
```

## Source


[busylight](https://github.com/JnyJny/busylight.git)

**Usage**:

```console
$ busylight [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-l, --light-id INTEGER`: Which light to operate on, see list output.  [default: 0]
* `-a, --all`: Operate on all lights.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `blink`: Activate the selected light in blink mode.
* `list`: List available lights (currently connected).
* `off`: Turn selected lights off.
* `on`: Turn selected lights on.
* `serve`: Start a FastAPI-based service to access...
* `supported`: List supported LED lights.
* `udev-rules`: Generate a Linux udev rules file.

## `busylight blink`

Activate the selected light in blink mode.

The light selected will blink with the specified color. The default color is red
if the user omits the color argument. Colors can be specified with color names and
hexadecimal values. Both '0x' and '#' are recognized as hexidecimal number prefixes
and hexadecimal values may be either three or six digits long.

Note: Ironically, BlinkStick products cannot be configured to blink on and off
      without software constantly updating the devices. If you need your BlinkStick
      to blink, you will need to use the `busylight serve` web API.

Examples:

```console
$ busylight blink          # light is blinking with the color red
$ busylight blink green    # now it's blinking green
$ busylight blink 0x00f    # now it's blinking blue
$ busylight blink #ffffff  # now it's blinking white
$ busylight --all blink    # now all available lights are blinking red
$ busylight --all off      # that's enough of that!
```

**Usage**:

```console
$ busylight blink [OPTIONS] [COLOR] [[slow|medium|fast]]
```

**Options**:

* `--help`: Show this message and exit.

## `busylight list`

List available lights (currently connected).
    

**Usage**:

```console
$ busylight list [OPTIONS]
```

**Options**:

* `-l, --long`
* `--help`: Show this message and exit.

## `busylight off`

Turn selected lights off.

To turn off all lights, specify --all:

```console
$ busylight --all off
```

**Usage**:

```console
$ busylight off [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `busylight on`

Turn selected lights on.

The light selected is turned on with the specified color. The default color is green
if the user omits the color argument. Colors can be specified with color names and
hexadecimal values. Both '0x' and '#' are recognized as hexidecimal number prefixes
and hexadecimal values may be either three or six digits long. 

Examples:


```console
$ busylight on          # light activated with the color green
$ busylight on red      # now it's red
$ busylight on 0x00f    # now it's blue
$ busylight on #ffffff  # now it's white
$ busylight --all on    # now all available lights are green
```

**Usage**:

```console
$ busylight on [OPTIONS] [COLOR]
```

**Options**:

* `--help`: Show this message and exit.

## `busylight serve`

Start a FastAPI-based service to access lights.

All connected lights are managed by the service, allowing
long-running animations and effects that the native device APIs
might not support.

Once the service is started, the API documentation is available
via these two URLs:


- `http://<hostname>:<port>/docs`
- `http://<hostname>:<port>/redoc`

## Examples


```console
$ busylight server >& log &
$ curl http://localhost:8888/1/lights
$ curl http://localhost:8888/1/lights/on
$ curl http://localhost:8888/1/lights/off
$ curl http://localhost:8888/1/light/0/on/purple
$ curl http://localhost:8888/1/light/0/off
$ curl http://localhost:8888/1/lights/on
$ curl http://localhost:8888/1/lights/off

**Usage**:

```console
$ busylight serve [OPTIONS]
```

**Options**:

* `-H, --host TEXT`
* `-p, --port INTEGER`
* `--help`: Show this message and exit.

## `busylight supported`

List supported LED lights.
    

**Usage**:

```console
$ busylight supported [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `busylight udev-rules`

Generate a Linux udev rules file.

Linux uses the udev subsystem to manage USB devices as they are
plugged and unplugged. By default, only the root user has read and
write access. The rules generated grant read/write access to all users
for all known USB lights by vendor id. Modify the rules to suit your
particular environment.

### Example


```console
$ busylight udev-rules -o 99-busylight.rules
$ sudo cp 99-busylight.rules /etc/udev/rules.d
```

**Usage**:

```console
$ busylight udev-rules [OPTIONS]
```

**Options**:

* `-o, --output PATH`: Save rules to this file.
* `--help`: Show this message and exit.

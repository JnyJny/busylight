# `busylight`

Control USB attached LED lights like a Human™

Make a USB attached LED light turn on, off and blink; all from the
comfort of your very own command-line. If your platform supports
HIDAPI (Linux, MacOS, Windows and probably others), then you can use
busylight with supported lights!

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

The light selected will blink with the specified color. The default
color is red if the user does not supply the color argument. Colors
can be specified with color names and hexadecimal values. Both '0x'
and '#' are recognized as hexidecimal number prefixes and
hexadecimal values may be either three or six digits long.

Note: Ironically, BlinkStick products cannot be configured to blink
      on and off without software constantly updating the
      devices. If you need your BlinkStick to blink, you will need
      to use the `busylight serve` web API.

Examples:


```
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

* `-l, --long`: Display more information about each light.
* `--help`: Show this message and exit.

## `busylight off`

Turn selected lights off.

Examples:


```
$ busylight off         # turn off light zero
$ busylight -l 0 off    # also turns off light zero
$ busylight --all off   # turns off all connected lights
```

**Usage**:

```console
$ busylight off [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `busylight on`

Turn selected lights on.

The light selected is turned on with the specified color. The
default color is green if the user does not supply the color
argument. Colors can be specified with color names and hexadecimal
values. Both '0x' and '#' are recognized as hexadecimal number
prefixes and hexadecimal values may be either three or six digits
long.

Examples:


```
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


```
- `http://<hostname>:<port>/docs`
- `http://<hostname>:<port>/redoc`
```

Examples:


```
$ busylight server >& log &
$ curl http://localhost:8888/1/lights
$ curl http://localhost:8888/1/lights/on
$ curl http://localhost:8888/1/lights/off
$ curl http://localhost:8888/1/light/0/on/purple
$ curl http://localhost:8888/1/light/0/off
$ curl http://localhost:8888/1/lights/on
$ curl http://localhost:8888/1/lights/off
```

**Usage**:

```console
$ busylight serve [OPTIONS]
```

**Options**:

* `-H, --host TEXT`: Hostname to bind the server to.  [default: 0.0.0.0]
* `-p, --port INTEGER`: Network port number to listen on  [default: 8888]
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

Example:


```
$ busylight udev-rules -o 99-busylight.rules
$ sudo cp 99-busylight.rules /etc/udev/rules.d
$ sudo udevadm control -R
# unplug/plug USB devices
```

**Usage**:

```console
$ busylight udev-rules [OPTIONS]
```

**Options**:

* `-o, --output PATH`: Save udev rules to this file.
* `--help`: Show this message and exit.

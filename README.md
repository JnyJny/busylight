# `busylight`

Control USB attached LED lights like a Human™

![Two Lights at Once](https://github.com/JnyJny/busylight/raw/master/demo/demo.gif)

Make a supported USB attached LED light turn on, off and blink; all
from the comfort of your very own command-line. If your platform
supports HIDAPI (Linux, MacOS, Windows and probably others), then
you can use `busylight`!

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
Embrava BlyncLight
Luxafor Flag
```

## Install


```console
$ pip install -U busylight-for-humans
$ busylight --help
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
* `supported`: List supported LED lights.

## `busylight blink`

Activate the selected light in blink mode.

The light selected will blink with the specified color. The default color is red
if the user omits the color argument. Colors can be specified with color names and
hexadecimal values. Both '0x' and '#' are recognized as hexidecimal number prefixes
and hexadecimal values may be either three or six digits long. 

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
$ busylight blink [OPTIONS] [COLOR]
```

**Options**:

* `-s, --speed`: Blink speed
* `--help`: Show this message and exit.

## `busylight list`

List available lights (currently connected).
    
    

**Usage**:

```console
$ busylight list [OPTIONS]
```

**Options**:

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

## `busylight supported`

List supported LED lights.
    

**Usage**:

```console
$ busylight supported [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

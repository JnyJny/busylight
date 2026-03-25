# Command Reference

Complete reference for all `busylight` subcommands.

## on

Turn lights on with specified color.

### Syntax

```bash
busylight on [COLOR] [OPTIONS]
```

### Arguments

- `COLOR` - Color specification (default: green)

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--led` | int | Target LED index (0=all, 1+=specific) |

### Examples

```bash
# Basic usage
busylight on                    # Green (default)
busylight on red                # Red
busylight on "#ff0000"          # Red (hex)

# LED targeting
busylight on red --led 1        # Top LED only
busylight on blue --led 2       # Bottom LED only
```

## off

Turn lights off.

### Syntax

```bash
busylight off
```

### Examples

```bash
busylight off                   # Turn off all lights
busylight --lights 0 off        # Turn off first light only
```

## blink

Create blinking effect alternating between color and off.

### Syntax

```bash
busylight blink [COLOR] [OPTIONS]
```

### Arguments

- `COLOR` - Blink color (default: red)

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--count` / `-c` | int | Number of blinks (0=infinite) |
| `--speed` / `-s` | choice | Blink speed (slow, medium, fast) |
| `--led` | int | Target LED index (0=all, 1+=specific) |

### Examples

```bash
# Basic blinking
busylight blink                 # Red, slow, infinite
busylight blink blue            # Blue, slow, infinite
busylight blink green --count 5 # Green, 5 blinks

# Speed control
busylight blink red --speed fast
busylight blink yellow --speed medium

# LED targeting
busylight blink red --led 1 --count 3
```

## rainbow

Rainbow color cycling effect.

### Syntax

```bash
busylight rainbow [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--speed` / `-s` | choice | Effect speed (slow, medium, fast) |

### Examples

```bash
busylight rainbow               # Default speed
busylight rainbow --speed fast  # Fast rainbow
```

## pulse

Pulsing/breathing effect with gradual brightness changes.

### Syntax

```bash
busylight pulse [COLOR] [OPTIONS]
```

### Arguments

- `COLOR` - Pulse color (default: red)

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--count` / `-c` | int | Number of pulses (0=infinite) |
| `--speed` / `-s` | choice | Pulse speed (slow, medium, fast) |

### Examples

```bash
busylight pulse                 # Red pulse
busylight pulse blue --count 3  # Blue, 3 pulses
busylight pulse green --speed fast
```

## fli

Flash Lights Impressively - alternates between two colors.

### Syntax

```bash
busylight fli [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--color1` | str | First color (default: red) |
| `--color2` | str | Second color (default: blue) |
| `--count` / `-c` | int | Number of flashes (0=infinite) |
| `--speed` / `-s` | choice | Flash speed (slow, medium, fast) |

### Examples

```bash
busylight fli                   # Red/blue alternating
busylight fli --color1 green --color2 yellow
busylight fli --count 10 --speed fast
```

## list

Display connected light devices.

### Syntax

```bash
busylight list [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--verbose` / `-v` | flag | Show detailed device information |

### Examples

```bash
busylight list                  # Basic device list
busylight list --verbose        # Detailed information
```

### Sample Output

```
Connected Lights:
0: Blink(1) mk2
1: BlinkStick Square
```

With `--verbose`:

```
Connected Lights:
0: Blink(1) mk2
   Path: /dev/hidraw0
   Vendor ID: 0x27B8
   Product ID: 0x01ED
   Serial: ABC123

1: BlinkStick Square  
   Path: /dev/hidraw1
   Vendor ID: 0x20A0
   Product ID: 0x41E5
   Serial: DEF456
```

## udev-rules

Generate Linux udev rules for USB device access.

### Syntax

```bash
busylight udev-rules [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--output` / `-o` | str | Output file name |

### Examples

```bash
# Output to stdout
busylight udev-rules

# Save to file
busylight udev-rules -o 99-busylights.rules

# Install (requires root)
busylight udev-rules -o 99-busylights.rules
sudo cp 99-busylights.rules /etc/udev/rules.d/
sudo udevadm control -R
```

## Global Options Reference

These options apply to all commands:

| Option | Type | Description |
|--------|------|-------------|
| `--all` | flag | Target all connected lights |
| `--lights` | str | Comma-separated light indices |
| `--timeout` | float | Operation timeout in seconds |
| `--dim` | float | Brightness factor (0.0-1.0) |
| `--debug` | flag | Enable debug logging |
| `--help` | flag | Show help message |

### Examples

```bash
# Target all lights
busylight --all on red

# Target specific lights
busylight --lights 0,2 blink blue

# Dim to 25%
busylight --dim 0.25 on white

# Debug mode
busylight --debug list
```
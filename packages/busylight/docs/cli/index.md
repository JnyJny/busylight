# Command Line Interface

The `busylight` command provides control over USB LED lights through various
subcommands. All commands support color specification and device targeting.

## Global Options

| Option | Description |
|--------|-------------|
| `--all` | Target all connected lights |
| `--lights INDEX` | Target specific lights by index (comma-separated) |
| `--timeout SECONDS` | Set operation timeout |
| `--dim FACTOR` | Brightness scaling (0.0-1.0) |
| `--debug` | Enable debug logging |

## Available Commands

| Command | Purpose |
|---------|---------|
| [`on`](commands.md#on) | Turn lights on with specified color |
| [`off`](commands.md#off) | Turn lights off |
| [`blink`](commands.md#blink) | Create blinking effect |
| [`rainbow`](commands.md#rainbow) | Rainbow color cycling effect |
| [`pulse`](commands.md#pulse) | Pulsing/breathing effect |
| [`fli`](commands.md#fli) | Flash Lights Impressively (two-color blink) |
| [`list`](commands.md#list) | Show connected devices |
| [`udev-rules`](commands.md#udev-rules) | Generate Linux udev rules |

## Color Specification

Colors can be specified in multiple formats:

```bash
# Named colors
busylight on red
busylight on green
busylight on blue

# Hex values
busylight on "#ff0000"    # Red
busylight on "#00ff00"    # Green  
busylight on "0x0000ff"   # Blue

# RGB tuples (programmatic)
busylight on "rgb(255,0,0)"  # Red
```

## Device Targeting

### All Devices

```bash
# Target all connected lights
busylight --all on red
busylight --all off
```

### Specific Devices

```bash
# Target first light (index 0)
busylight --lights 0 on blue

# Target multiple lights
busylight --lights 0,2 blink green

# List devices to see indices
busylight list
```

### LED Targeting (Multi-LED Devices)

For devices with multiple LEDs (Blink1 mk2, BlinkStick variants):

```bash
# Control all LEDs (default)
busylight on red

# Control specific LED
busylight on red --led 1     # Top/first LED
busylight on blue --led 2    # Bottom/second LED

# Blink specific LED
busylight blink green --led 1 --count 5
```

## Common Usage Patterns

### Status Indication

```bash
# Success (green)
busylight on green

# Warning (yellow/amber)
busylight on yellow

# Error (red)
busylight on red

# Processing (blue blink)
busylight blink blue
```

### Meeting Status

```bash
# Available
busylight on green

# Busy  
busylight on red

# Do not disturb
busylight blink red --count 3

# In meeting
busylight rainbow
```

### Build Status Integration

```bash
# Build started
busylight blink yellow

# Build passed
busylight on green

# Build failed
busylight blink red --count 5

# Build stopped
busylight off
```

## Advanced Features

### Brightness Control

```bash
# Dim to 50%
busylight --dim 0.5 on red

# Very dim (10%)
busylight --dim 0.1 on blue
```

### Timeouts

```bash
# Timeout after 30 seconds
busylight --timeout 30 blink red

# No timeout (indefinite)
busylight --timeout 0 rainbow
```

### Debug Output

```bash
# Show detailed information
busylight --debug list
busylight --debug on red
```

## Error Handling

The CLI provides clear error messages:

- **No devices found**: Check connections and udev rules (Linux)
- **Invalid color**: Use supported color names or hex values
- **Device unavailable**: Device may be in use by another process
- **Permission denied**: Install udev rules (Linux) or run with elevated
  privileges

For detailed troubleshooting, use the `--debug` flag to see diagnostic
information.

## Advanced Topics

- **[Light Selection Guide](selection-guide.md)** - Comprehensive guide to targeting specific lights in multi-device setups
- **[Command Reference](commands.md)** - Complete list of available commands and options  
- **[Usage Examples](examples.md)** - Real-world integration scenarios and automation patterns
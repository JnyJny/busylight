# Installation

## Requirements

- Python 3.11 or higher
- USB LED light device
- macOS or Linux (Windows support in development)

## Basic Installation

The basic installation includes the `busylight` command-line tool.

### Using pip

```bash
pip install busylight-for-humans
```

### Using uvx

```bash
uvx --from busylight-for-humans busylight list
```

## Web API Installation

To use the HTTP API server, install with web API dependencies.

### Using pip

```bash
pip install busylight-for-humans[webapi]
```

### Using uvx

```bash
uvx --from "busylight-for-humans[webapi]" busyserve
```

## Development Installation

For development, use [uv](https://docs.astral.sh/uv/) for dependency
management.

```bash
# Install uv
pip install uv

# Clone repository
git clone https://github.com/JnyJny/busylight.git
cd busylight

# Install with all dependencies
uv sync --all-extras
source .venv/bin/activate

# Verify installation
busylight --help
busyserve --help
pytest
```

## Platform-Specific Setup

### Linux (udev rules)

Linux requires udev rules for USB device access. Run these commands with
root privileges:

```bash
# Generate udev rules
busylight udev-rules -o 99-busylights.rules

# Install rules
sudo cp 99-busylights.rules /etc/udev/rules.d/
sudo udevadm control -R

# Unplug and reconnect your light
busylight on
```

### macOS

No additional setup required. The system may prompt for permission to
access USB devices.

### Windows

Windows support is in development. Basic functionality may work, but full
compatibility is not guaranteed.

## Verification

Test your installation:

```bash
# List connected lights
busylight list

# Turn on first light
busylight on

# Start web API (if installed)
busyserve --help
```

## Troubleshooting

### No lights found

1. Verify device is connected via USB
2. Check device compatibility in [supported devices](devices/index.md)
3. On Linux, ensure udev rules are installed
4. Try running with `--debug` flag for detailed output

### Permission errors

- **Linux**: Install udev rules as shown above
- **macOS**: Grant USB device permissions when prompted
- **Windows**: Run as administrator (experimental)

### Import errors

Ensure you have the correct optional dependencies:

```bash
# For web API features
pip install busylight-for-humans[webapi]

# For development
pip install busylight-for-humans[webapi,docs]
```
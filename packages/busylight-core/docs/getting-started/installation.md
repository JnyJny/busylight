# Installation

Busylight Core requires Python 3.11 or later.

## Install from PyPI

The easiest way to install busylight_core is from PyPI:

```bash
pip install busylight_core
```

## Install from Source

You can also install from source:

```bash
git clone https://github.com/JnyJny/busylight_core.git
cd busylight_core
pip install -e .
```

## Development Installation

For development, we recommend using `uv`:

```bash
git clone https://github.com/JnyJny/busylight_core.git
cd busylight_core
uv sync
```

This will install all dependencies including development tools.

## Verify Installation

After installation, verify that busylight_core is working by running the test suite:

```bash
pytest
```

If you don't have pytest installed, install it first:

```bash
pip install pytest
```

You can also do a quick import test to verify the library is installed correctly:

```python
from busylight_core import Light
print("busylight_core imported successfully")
```

## Linux Setup (udev Rules)

On Linux, you need to configure udev rules to allow non-root access to USB
devices. This is the most common setup requirement for Linux users.

### Quick Setup

The library can generate the correct udev rules for you:

```python
from busylight_core import Light

# Generate rules for all supported devices
rules = Light.udev_rules()

# Print rules to copy to a file
for device_ids, rule_lines in rules.items():
    for line in rule_lines:
        print(line)
```

### Manual Setup

1. **Create the udev rules file** (requires sudo):

```bash
sudo touch /etc/udev/rules.d/99-busylight.rules
```

2. **Add rules for your device**. Here are rules for common devices:

```bash
# Embrava Blynclight devices
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0e53", ATTRS{idProduct}=="2516", MODE="0666"
KERNEL=="hidraw*", ATTRS{idVendor}=="0e53", ATTRS{idProduct}=="2516", MODE="0666"

# Kuando Busylight Alpha
SUBSYSTEMS=="usb", ATTRS{idVendor}=="27bb", ATTRS{idProduct}=="3bca", MODE="0666"
KERNEL=="hidraw*", ATTRS{idVendor}=="27bb", ATTRS{idProduct}=="3bca", MODE="0666"

# Luxafor Flag
SUBSYSTEMS=="usb", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="f372", MODE="0666"
KERNEL=="hidraw*", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="f372", MODE="0666"

# ThingM Blink1 
SUBSYSTEMS=="usb", ATTRS{idVendor}=="27b8", ATTRS{idProduct}=="01ed", MODE="0666"
KERNEL=="hidraw*", ATTRS{idVendor}=="27b8", ATTRS{idProduct}=="01ed", MODE="0666"
```

3. **Reload udev rules**:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

4. **Unplug and reconnect your device** for the rules to take effect.

### Troubleshooting Linux Setup

**Device not detected?**
- Check if your device is connected: `lsusb | grep -i busylight`
- Verify udev rules are loaded: `udevadm info --name=/dev/hidraw0 --attribute-walk`
- Check device permissions: `ls -la /dev/hidraw*`

**Permission denied errors?**
- Ensure udev rules are in `/etc/udev/rules.d/` with `.rules` extension
- Verify rules syntax with `udevadm test /sys/class/hidraw/hidraw0`
- Add your user to `input` group: `sudo usermod -a -G input $USER` (logout/login required)

## Next Steps

Now that you have busylight_core installed, check out the [Quick Start](quickstart.md) guide to learn how to use it.

# Configuration

Busylight Core is a Python library for controlling USB status lights. It does not require external configuration files.

## Library Usage

Import and use the library directly in your Python code:

```python
from busylight_core import Light, NoLightsFoundError

try:
    light = Light.first_light()
    light.on((255, 0, 0))
    light.off()
except NoLightsFoundError:
    print("No lights found")
```

## Device Initialization

All Light devices support `reset` and `exclusive` parameters during initialization:

```python
from busylight_core import Light, NoLightsFoundError

try:
    # Standard initialization - resets device and acquires exclusive access
    light = Light.first_light()

    # Explicitly control initialization behavior
    light = Light.first_light(reset=True, exclusive=True)    # Default behavior
    light = Light.first_light(reset=False, exclusive=False)  # No reset, shared access

except NoLightsFoundError:
    print("No lights found")
```

**Parameters:**
- `reset=True`: Reset device to known state during initialization (default)
- `exclusive=True`: Acquire exclusive access to prevent interference (default)

## Logging

Busylight Core uses [loguru](https://loguru.readthedocs.io/) for logging. Control logging output:

```python
from loguru import logger
from busylight_core import Light

# Enable busylight_core logging (disabled by default)
logger.enable("busylight_core")

# Use the library - debug information will now be shown
lights = Light.all_lights()

# Disable logging again
logger.disable("busylight_core")
```

## Next Steps

- Learn about device capabilities in [Device Capabilities](../user-guide/device-capabilities.md)
- See usage examples in [Examples](../user-guide/examples.md)
- Check the [API Reference](../reference/index.md) for complete method documentation

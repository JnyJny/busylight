# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install uv package manager
python3 -m pip install uv

# Set up development environment
uv venv .venv
source .venv/bin/activate
uv sync --all-extras
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=./src/busylight --cov-report=html

# Run specific test file
pytest tests/test_manager.py

# Run specific test function
pytest tests/test_manager.py::test_function_name
```

### Code Quality
```bash
# Format code
ruff format src/busylight tests

# Fix import sorting
ruff check --select I --fix src/busylight tests

# Type checking
mypy --config-file pyproject.toml src/busylight

# Run all linting
ruff check src/busylight tests
```

### Build and Distribution
```bash
# Build package
uv build

# Clean build artifacts
rm -rf htmlcov dist busylight.egg-info *.log
```

### Project Scripts
The project includes two main CLI tools:
- `busylight` - Main CLI for controlling lights
- `busyserve` - Web API server for HTTP control

## Architecture Overview

### Core Components

1. **Light Abstraction System**: The project uses an ABC-based system where `Light` is the base abstract class that all physical light implementations inherit from. Light subclasses are automatically discovered via `__subclasses__()`.

2. **Device Categories**: 
   - **HIDLight**: USB HID-based devices (most common)
   - **SerialLight**: Serial port-based devices
   - Physical light classes inherit from these base classes

3. **Vendor Support**: Each vendor has its own package under `src/busylight/lights/` with device-specific implementations:
   - `embrava/` - Blynclight series
   - `kuando/` - Busylight Alpha/Omega
   - `luxafor/` - Flag, Mute, Orb, Bluetooth
   - `thingm/` - Blink(1) devices
   - `agile_innovative/` - BlinkStick
   - `muteme/`, `mutesync/`, `compulab/`, `plantronics/`, `busytag/`

4. **Effects System**: `BaseEffect` abstract class with implementations for:
   - `Steady` - solid color
   - `Blink` - on/off blinking
   - `Spectrum` - rainbow cycling
   - `Gradient` - color transitions

5. **Manager System**: `LightManager` handles multiple lights with:
   - Device discovery and enumeration
   - Async task management via `TaskableMixin`
   - Batch operations across multiple devices
   - Device state monitoring (plugged/unplugged)

6. **Web API**: FastAPI-based REST interface in `api/` directory with Pydantic models for validation.

### Key Design Patterns

- **Factory Pattern**: `Light.first_light()` and `Light.all_lights()` for device discovery
- **Strategy Pattern**: Different read/write strategies for HID vs Serial devices
- **Context Manager**: `exclusive_access()` and `batch_update()` for device I/O
- **Async/Await**: Effects run as async tasks for non-blocking operation
- **Plugin Architecture**: Vendor-specific implementations auto-discovered via inheritance

### Platform Support
- Primary: macOS and Linux
- Windows: Untested but reported working
- Linux requires udev rules for USB device access

### Color System
- RGB tuples: `(red, green, blue)` with values 0-255
- Support for named colors via `webcolors` library
- Hex color support: `#RRGGBB` format

### Configuration
- Uses `pyproject.toml` with `uv` for dependency management
- Development dependencies include testing, linting, and type checking tools
- Optional `webapi` dependency group for HTTP server functionality
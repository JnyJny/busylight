# Contributing to BusyLight

Thank you for your interest in contributing to BusyLight! This guide provides
everything you need to set up a development environment and contribute
effectively.

## Overview

BusyLight provides user interfaces for USB LED lights via
[busylight-core][busylight-core]. The core library handles device
communication; this project provides CLI and HTTP API interfaces.

## Quick Start

### Prerequisites

- **uv**
- **Git** for version control
- **USB LED device** for testing (optional but recommended)

### Development Setup

#### Clone
```bash
# Clone the repository
git clone https://github.com/JnyJny/busylight.git
cd busylight
```

#### Install UV
```bash
# Install uv (modern Python package manager)
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```console
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Configure Development Virtual Environment
```bash
# Create virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --all-extras
```

#### Confirm Installatio
```bash
# Verify installation
which busylight
which busyserve
busylight list
```

The project installs in editable mode - source changes are reflected
immediately when running in the virtual environment.

## Development Commands

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_main.py

# Run with coverage report
poe coverage  # Opens HTML coverage report

# Run specific test pattern
pytest -k "test_light_manager"
```

### Code Quality

```bash
# Format code (ruff + docformatter)
poe format

# Lint code (ruff check)
poe check

# Format and lint together
poe ruff

# Type checking
ty src/
```

### Build & Package

```bash
# Build package
uv build

# Clean build artifacts
poe clean

# Version bump and publish (maintainers only)
poe publish
```

### Documentation

```bash
# Install docs dependencies
uv sync --extra docs

# Build documentation locally
mkdocs serve

# Build for deployment
mkdocs build
```

## Architecture

### Project Structure

```
busylight/
├── src/busylight/          # Main package
│   ├── api/                # FastAPI web server
│   ├── cli/                # Command-line interface
│   ├── effects/            # LED effects (blink, pulse, etc.)
│   └── manager.py          # Light coordination
├── tests/                  # Test suite
├── docs/                   # MkDocs documentation
├── pyproject.toml          # Project configuration
└── CONTRIBUTING.md         # This file
```

### Core Components

#### **busylight-core Integration**
- Handles device discovery and USB/Serial communication
- Vendor-specific protocols and device drivers
- Low-level LED control operations

#### **Interfaces**
- **CLI (`busylight`)**: Command-line tool for direct control
- **HTTP API (`busyserve`)**: REST endpoints for automation

#### **Effects System**
- **Steady**: Static colors with brightness control
- **Blink**: Flashing effects with configurable timing
- **Spectrum**: Color cycling and rainbow effects
- **Gradient**: Smooth color transitions

#### **Light Manager**
- Coordinates multiple devices simultaneously
- Async task management for non-blocking effects
- Batches operations for better performance

#### **Web API**
- FastAPI framework with Pydantic models
- JSON responses with comprehensive error handling
- Optional HTTP Basic Authentication

### Design Patterns

- **Facade/Adapter**: Simplifies busylight-core interface
- **Async/Await**: Non-blocking effects and concurrent operations
- **Dependency Injection**: Testable components with clear interfaces

## Effects Development

The Effects system is the core of BusyLight's dynamic lighting capabilities.
Understanding how to create and modify effects is essential for contributors.

### Effects Architecture

All effects inherit from `BaseEffect` in `src/busylight/effects/effect.py`:

```python
class BaseEffect(abc.ABC):
    @property
    @abc.abstractmethod
    def colors(self) -> list[tuple[int, int, int]]:
        """List of RGB color tuples defining the effect sequence."""
    
    @property
    @abc.abstractmethod  
    def default_interval(self) -> float:
        """Default interval between color changes in seconds."""
```

### Built-in Effects

- **`Steady`**: Static color display
- **`Blink`**: Alternates between two colors
- **`Spectrum`**: Rainbow color cycling with sine wave generation
- **`Gradient`**: Smooth fade from black to color and back

### Creating New Effects

#### 1. Basic Effect Structure

```python
from typing import TYPE_CHECKING
from busylight_core.mixins.taskable import TaskPriority
from busylight.effects.effect import BaseEffect

if TYPE_CHECKING:
    from busylight_core import Light

class MyEffect(BaseEffect):
    def __init__(self, color: tuple[int, int, int]) -> None:
        self.color = color
        self.priority = TaskPriority.NORMAL
    
    @property
    def colors(self) -> list[tuple[int, int, int]]:
        # Return your color sequence
        return [self.color, (0, 0, 0)]  # Color + black
    
    @property
    def default_interval(self) -> float:
        return 0.5  # 500ms between changes
```

#### 2. Color Generation Patterns

**Static Sequences:**
```python
@property
def colors(self) -> list[tuple[int, int, int]]:
    return [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
```

**Computed Sequences:**
```python
@property
def colors(self) -> list[tuple[int, int, int]]:
    if hasattr(self, "_colors"):
        return self._colors
    
    # Generate color sequence
    colors = []
    for i in range(10):
        intensity = int(255 * (i / 10))
        colors.append((intensity, 0, 0))
    
    self._colors = colors  # Cache result
    return self._colors
```

**Mathematical Functions:**
```python
import math

@property  
def colors(self) -> list[tuple[int, int, int]]:
    colors = []
    for i in range(50):
        # Sine wave for smooth transitions
        r = int(127 * math.sin(i * 0.1) + 128)
        g = int(127 * math.cos(i * 0.1) + 128)
        colors.append((r, g, 0))
    return colors
```

#### 3. Advanced Execution Control

For complex timing or custom logic, override `execute()`:

```python
async def execute(self, light: "Light", interval: float | None = None) -> None:
    """Custom execution with variable timing."""
    try:
        for i, color in enumerate(self.colors):
            light.on(color)
            
            # Variable timing based on position
            if i % 2 == 0:
                await asyncio.sleep(0.1)  # Fast
            else:
                await asyncio.sleep(0.5)  # Slow
                
    finally:
        light.off()  # Always cleanup
```

### Effect Development Guidelines

#### Performance Best Practices

1. **Cache Color Calculations**: Use `self._colors` to avoid recomputation
2. **Reasonable Sequence Length**: Keep under 1000 colors for performance
3. **Appropriate Timing**: Balance smoothness with device capabilities
4. **Memory Efficiency**: Generate colors lazily when possible

#### Testing Effects

**Unit Tests:**
```python
def test_effect_colors():
    effect = MyEffect(color=(255, 0, 0))
    colors = effect.colors
    
    assert len(colors) > 0
    assert all(len(color) == 3 for color in colors)
    assert all(0 <= c <= 255 for color in colors for c in color)

async def test_effect_execution():
    effect = MyEffect(color=(255, 0, 0))
    mock_light = Mock()
    
    await effect.execute(mock_light)
    assert mock_light.on.called
    assert mock_light.off.called
```

**Integration Testing:**
```bash
# Test with actual hardware
busylight --debug on red  # Test steady effect
busylight --debug blink blue --count 3  # Test blink effect
```

#### Effect Registration

Add new effects to `src/busylight/effects/__init__.py`:

```python
from .my_effect import MyEffect

__all__ = [
    "Blink",
    "Effects",
    "Gradient", 
    "MyEffect",  # Add here
    "Spectrum",
    "Steady",
]
```

#### CLI Integration

Effects are automatically available via the discovery system:

```python
# In CLI code
effect_class = BaseEffect.for_name("myeffect")
effect = effect_class(color=(255, 0, 0))
```

### Effect Debugging

#### Common Issues

**Colors Not Displaying:**
- Verify RGB values are 0-255
- Check that `colors` property returns non-empty list
- Ensure `default_interval` > 0

**Performance Problems:**
- Profile color generation with large sequences
- Cache expensive computations in `_colors`
- Use appropriate sleep intervals

**Memory Leaks:**
- Clear cached data in `reset()` method if needed
- Avoid circular references in effect objects

#### Debug Utilities

```python
# Add to effect class for debugging
def debug_info(self) -> dict:
    return {
        "name": self.name,
        "color_count": len(self.colors),
        "interval": self.default_interval,
        "priority": self.priority.name,
    }
```

### Effect Examples

See **[complete effects documentation][docs-effects]** for:
- Detailed API reference
- Advanced color generation techniques
- Mathematical effect patterns
- Performance optimization strategies
- Integration examples

Contributing new effects expands BusyLight's creative possibilities and
benefits the entire community!

## Development Workflow

### 1. Issue First

Before starting work:
- Check [existing issues][issues] for duplicates
- Open an issue to discuss new features or large changes
- Get feedback before implementing significant changes

### 2. Branch Strategy

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/issue-description
```

### 3. Development Process

1. **Write Tests First** (TDD approach recommended)
2. **Implement Feature** with comprehensive error handling
3. **Update Documentation** if APIs or behavior change
4. **Run Quality Checks** before committing

```bash
# Pre-commit checklist
poe ruff        # Format and lint
pytest          # All tests pass
ty src/       # Type checking
```

### 4. Commit Guidelines

Follow conventional commit format:

```bash
# Feature commits
git commit -m "feat: add support for new LED device"

# Bug fixes
git commit -m "fix: resolve color parsing for hex values"

# Documentation
git commit -m "docs: update API examples"

# Refactoring
git commit -m "refactor: simplify light manager initialization"

# Tests
git commit -m "test: add coverage for multi-LED targeting"
```

### 5. Pull Request Process

1. **Push branch** to your fork
2. **Open PR** with clear description
3. **Link related issues** using `Fixes #123`
4. **Wait for CI** to pass all checks
5. **Address feedback** from code review
6. **Squash commits** if requested before merge

## Testing Guidelines

### Test Structure

```python
# tests/test_example.py
import pytest
from busylight.manager import LightManager

class TestLightManager:
    def test_initialization(self):
        """Test basic manager setup."""
        manager = LightManager()
        assert manager is not None
    
    def test_device_discovery(self, mock_devices):
        """Test device detection with mocked hardware."""
        # Test implementation
        pass
```

### Testing Best Practices

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Mock Hardware**: Use fixtures for device simulation
- **Edge Cases**: Test error conditions and boundary values
- **Async Tests**: Use `pytest-asyncio` for async components

### Running Specific Tests

```bash
# Test specific module
pytest tests/test_manager.py

# Test with specific marker
pytest -m "not slow"

# Test with pattern matching
pytest -k "manager and not async"

# Debug single test
pytest tests/test_manager.py::TestLightManager::test_initialization -v
```

## Code Style

### Python Standards

- **PEP 8**: Standard Python style (enforced by ruff)
- **Type Hints**: Use for all public APIs
- **Docstrings**: [Sphinx style][sphinx-docstrings] for all public functions
- **Error Handling**: Specific exceptions with clear messages

### Examples

```python
from typing import Optional, List
from busylight.exceptions import DeviceNotFoundError

def turn_on_light(
    light_id: int, 
    color: str = "green",
    brightness: float = 1.0
) -> bool:
    """Turn on specified light with given color and brightness.
    
    Args:
        light_id: Zero-based device index
        color: Color name, hex value, or RGB tuple
        brightness: Brightness factor between 0.0 and 1.0
        
    Returns:
        True if operation succeeded
        
    Raises:
        DeviceNotFoundError: If light_id is invalid
        ValueError: If color or brightness values are invalid
    """
    if not 0 <= brightness <= 1.0:
        raise ValueError(f"Brightness must be 0.0-1.0, got {brightness}")
    
    # Implementation here
    return True
```

## Platform Considerations

### macOS/Linux (Primary)

- Full USB device support
- No additional setup required
- All features available

### Linux-Specific

- **udev rules required** for USB access
- Generate with: `busylight udev-rules`
- Some devices need specific kernel modules

### Windows (Experimental)

- Limited device support
- May require additional drivers
- Test thoroughly before claiming compatibility

## Debugging

### Common Issues

**Device Not Found:**
```bash
# Check device detection
busylight list --debug

# Linux: verify udev rules
cat /etc/udev/rules.d/99-busylights.rules

# Check USB permissions
lsusb  # Linux
system_profiler SPUSBDataType  # macOS
```

**Import Errors:**
```bash
# Verify virtual environment
which python
pip list | grep busylight

# Reinstall in development mode
uv sync --all-extras
```

**Test Failures:**
```bash
# Run specific failing test with verbose output
pytest tests/test_failing.py::test_method -v -s

# Check test dependencies
pip install pytest pytest-asyncio pytest-mock
```

## Documentation

### Writing Documentation

- **MkDocs**: Documentation uses Material theme
- **Markdown**: Standard markdown with extensions
- **API Docs**: Auto-generated from docstrings
- **Examples**: Include working code samples

### Documentation Commands

```bash
# Serve locally with live reload
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages (maintainers)
mkdocs gh-deploy
```

## Release Process

### For Maintainers

```bash
# 1. Ensure clean working directory
git status

# 2. Run full test suite
pytest
poe coverage

# 3. Update version and publish
poe publish  # Bumps version, builds, publishes to PyPI and GitHub release.
```

### Version Strategy

- **Patch**: Bug fixes, documentation updates
- **Minor**: New features, non-breaking changes
- **Major**: Breaking API changes (rare)

Follows [Semantic Versioning][semver] principles.

## Community

### Getting Help

- **[GitHub Discussions][discussions]**: Community questions and ideas
- **[Issues][issues]**: Bug reports and feature requests
- **[Documentation][docs]**: Comprehensive guides and API reference

### Code of Conduct

This project follows the [Contributor Covenant][coc]. Please be respectful
and inclusive in all interactions.

## Hardware Support

### Adding New Devices

Device support is handled in [busylight-core][busylight-core]. To request
support for new hardware:

1. **[Open device request][device-request]** with device details
2. **Provide specifications**: USB vendor/product IDs, protocols
3. **Test device** if possible (we can arrange loaner devices)

### Testing with Hardware

- **Multiple devices**: Test with various vendor devices
- **LED targeting**: Verify multi-LED device support
- **Platform testing**: Test on different operating systems
- **Error conditions**: Test unplugging, invalid commands

## Troubleshooting

### Development Environment Issues

**Virtual Environment:**
```bash
# Remove and recreate
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv sync --all-extras
```

**Permission Issues (Linux):**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again

# Or run with sudo (not recommended)
sudo busylight list
```

**Import Path Issues:**
```bash
# Verify project is installed in development mode
pip show -f busylight-for-humans | grep Location
```

---

Thank you for contributing to BusyLight! Your efforts help make USB LED
control accessible to developers worldwide.

[busylight-core]: https://github.com/JnyJny/busylight-core
[issues]: https://github.com/JnyJny/busylight/issues
[discussions]: https://github.com/JnyJny/busylight/discussions
[device-request]: https://github.com/JnyJny/busylight-core/issues/new?template=4_new_device_request.yaml
[docs]: https://jnyjny.github.io/busylight/
[docs-effects]: https://jnyjny.github.io/busylight/effects/
[semver]: https://semver.org/
[sphinx-docstrings]: https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
[coc]: https://www.contributor-covenant.org/version/2/1/code_of_conduct/

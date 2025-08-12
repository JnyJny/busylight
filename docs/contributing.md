# Contributing to BusyLight

Thank you for your interest in contributing to BusyLight! This page provides
an overview of how to contribute. For detailed development setup and
guidelines, see the **[complete contributing guide][contributing-repo]**.

## Quick Start

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/JnyJny/busylight.git
cd busylight
python3 -m pip install uv
uv venv .venv && source .venv/bin/activate
uv sync --all-extras

# Verify installation
busylight list
pytest
```

## Ways to Contribute

### 🐛 Report Issues

Found a bug or have a feature request?

- **[Report Bug][issues]** - Include device details and error messages
- **[Request Feature][issues]** - Describe the use case and expected behavior
- **[Request Device Support][device-request]** - New hardware support

### 📝 Improve Documentation

- Fix typos or unclear explanations
- Add examples and use cases
- Update device compatibility information
- Improve API documentation

### 🔧 Code Contributions

- Bug fixes and performance improvements
- New features and LED effects
- Test coverage improvements
- Platform compatibility enhancements

### 💡 Share Ideas

- **[GitHub Discussions][discussions]** - Community questions and ideas
- Integration patterns and automation examples
- Hardware testing and device feedback

## Development Workflow

### 1. Setup Development Environment

See **[detailed setup guide][contributing-repo]** for complete instructions
including testing, code quality tools, and debugging tips.

### 2. Follow Coding Standards

- **Code Style**: Enforced by ruff formatter and linter
- **Type Hints**: Required for all public APIs
- **Testing**: Write tests for new features and bug fixes
- **Documentation**: Update docs for API changes

### 3. Submit Pull Requests

1. **Fork** the repository
2. **Create feature branch** from master
3. **Write tests** for your changes
4. **Run quality checks**: `poe ruff && pytest`
5. **Open pull request** with clear description

## Architecture Overview

### Project Structure

```
busylight/
├── src/busylight/          # Main package
│   ├── api/                # FastAPI web server
│   ├── cli/                # Command-line interface
│   ├── effects/            # LED effects
│   └── manager.py          # Device coordination
├── tests/                  # Test suite
├── docs/                   # Documentation
└── CONTRIBUTING.md         # Detailed contributing guide
```

### Key Components

- **busylight-core**: Device drivers and USB communication
- **CLI Interface**: Command-line tool (`busylight`)
- **Web API**: REST endpoints (`busyserve`)
- **Effects System**: Blink, pulse, rainbow, and custom effects
- **Light Manager**: Multi-device coordination and async effects

## Testing

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_manager.py

# Coverage report
poe coverage
```

### Testing Guidelines

- **Unit tests** for individual components
- **Integration tests** for component interactions
- **Mock hardware** for device simulation
- **Cross-platform testing** when possible

## Code Quality

```bash
# Format code
poe format

# Lint code
poe check

# Format and lint
poe ruff

# Type checking
mypy src/
```

## Documentation

### Local Development

```bash
# Install docs dependencies
uv sync --extra docs

# Serve with live reload
mkdocs serve

# Build static site
mkdocs build
```

### Documentation Guidelines

- **Clear examples** with working code
- **Complete API coverage** with parameter descriptions
- **Platform-specific notes** for setup differences
- **Integration guides** for common use cases

## Hardware Support

### Supported Devices

BusyLight supports 23 devices from 9 vendors. Device drivers are handled
by [busylight-core][busylight-core].

### Adding New Devices

1. **[Open device request][device-request]** with specifications
2. **Provide details**: USB vendor/product IDs, LED count, protocols
3. **Testing**: We can arrange loaner devices if needed

### Testing with Hardware

- Test with multiple vendor devices
- Verify multi-LED targeting functionality
- Cross-platform compatibility testing
- Error condition handling (unplugging, invalid commands)

## Community Guidelines

### Code of Conduct

This project follows the [Contributor Covenant][coc]. Please be respectful
and inclusive in all interactions.

### Getting Help

- **[Documentation][docs]** - Comprehensive guides and API reference
- **[GitHub Discussions][discussions]** - Community support
- **[Issues][issues]** - Bug reports and feature requests

## Development Commands Reference

```bash
# Development setup
uv sync --all-extras

# Code quality
poe ruff                # Format and lint
pytest                  # Run tests
poe coverage            # Test coverage

# Documentation
mkdocs serve            # Local docs server
mkdocs build            # Build docs

# Package building
uv build                # Build package
poe clean               # Clean artifacts
```

## Release Process

Releases are handled by project maintainers:

1. **Version bump** following [semantic versioning][semver]
2. **Comprehensive testing** across platforms and devices
3. **Documentation updates** for new features
4. **PyPI publication** via automated workflows

---

## Ready to Contribute?

📖 **[Read the complete contributing guide →][contributing-repo]**

The detailed guide includes:

- Complete development environment setup
- Testing strategies and debugging tips
- Code architecture and design patterns
- Platform-specific considerations
- Release and deployment processes

Thank you for helping make BusyLight better! 🚀

[contributing-repo]: https://github.com/JnyJny/busylight/blob/master/CONTRIBUTING.md
[busylight-core]: https://github.com/JnyJny/busylight-core
[issues]: https://github.com/JnyJny/busylight/issues
[device-request]: https://github.com/JnyJny/busylight-core/issues/new?template=4_new_device_request.yaml
[discussions]: https://github.com/JnyJny/busylight/discussions
[docs]: https://jnyjny.github.io/busylight/
[semver]: https://semver.org/
[coc]: https://www.contributor-covenant.org/version/2/1/code_of_conduct/
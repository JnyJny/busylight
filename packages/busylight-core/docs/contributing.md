# Contributing

We welcome contributions to busylight-core! This guide will help you get
started with development, testing, and submitting changes.

We have issues labeled as [Good First Issue][good-first-issue] and
[Help Wanted][help-wanted] which are good opportunities for new
contributors.

## Development Setup

### Prerequisites

- Python 3.11+ 
- [uv][astral-uv] for dependency management
- Git for version control
- Optional: [direnv][direnv] for automatic environment activation

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JnyJny/busylight-core.git
   cd busylight-core
   ```

2. **Install dependencies and create virtual environment:**
   ```bash
   uv sync --all-groups
   ```

3. **Optional: Enable direnv for automatic environment activation:**
   ```bash
   direnv allow
   ```

4. **Verify installation:**
   ```bash
   uv run poe test
   ```

## Development Workflow

### Available Commands

The project uses [Poe the Poet][poe-the-poet]  for task
automation. Run `poe` without arguments to see all available tasks:

**Code Quality:**
- `poe test` - Run test suite with pytest
- `poe ruff-check` - Run ruff linting checks
- `poe ruff-format` - Format code with ruff
- `poe ruff` - Run both check and format
- `poe coverage` - Generate and open HTML coverage report

**Development:**
- `poe docs-serve` - Serve documentation locally for development
- `poe docs-build` - Build documentation
- `poe clean` - Remove build artifacts and cache files

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b features/your-feature-name
   ```

2. **Make your changes** following the project conventions

3. **Run quality checks:**
   ```bash
   poe ruff        # Format and lint code
   poe test        # Run tests
   poe coverage    # Check test coverage
   ```

4. **Commit your changes** using conventional commit format (see below)

5. **Push and create a pull request**

## Testing

### Running Tests

The project uses pytest with coverage reporting:

```bash
# Run unit tests
poe test

# Run doc tests (validates all Python code blocks in docs/)
poe doc-test

# Run tests with coverage report
poe coverage

# Run specific test file
uv run pytest tests/test_specific.py

# Run tests with verbose output
uv run pytest -v
```

### Test Structure

- `tests/` - Main test directory
- `tests/vendor_examples/` - Vendor-specific test examples
- Tests follow the naming convention `test_*.py`
- Mock hardware devices are used for testing (no real hardware required)

### Doc Tests

All Python code blocks in `docs/` are automatically tested using
[pytest-markdown-docs][pytest-markdown-docs]. This catches hallucinated
or outdated API examples before they ship.

- Every fenced Python code block is executed during CI
- USB hardware is mocked via `docs/conftest.py` (no devices needed)
- If a block depends on imports from the previous block, use:
  `` ```python continuation ``
- To exclude a block from testing: `` ```python notest ``
- CI runs doc tests on every PR, push to main, and release

### Writing Tests

When adding new features:

1. **Create tests first** (TDD approach encouraged)
2. **Aim for >90% test coverage** for production code
3. **Test both success and error cases**
4. **Use descriptive test names** that explain the behavior being tested
5. **Mock hardware dependencies** - tests should not require real devices
6. **Update doc examples** - if you change an API, update the docs and
   the doc tests will catch any mismatches

Example test structure:
```python
def test_device_on_method_sets_color(self, mock_device) -> None:
    """Test that on() method properly sets device color."""
    mock_device.on((255, 0, 0))
    
    assert mock_device.color == (255, 0, 0)
```

## Architecture Overview

### Core Components

**busylight-core** provides a unified interface for controlling USB-connected
status lights through a plugin-style architecture:

1. **Light** (src/busylight_core/light.py) - Abstract base class for all devices
2. **Hardware** (src/busylight_core/hardware.py) - Hardware detection and connection
3. **Vendor implementations** (src/busylight_core/vendors/) - Device-specific classes
4. **Mixins** (src/busylight_core/mixins/) - Shared functionality (ColorableMixin, TaskableMixin)

### Adding Device Support

To add support for a new device:

1. **Create or use existing vendor package** in `src/busylight_core/vendors/`
2. **Implement Light subclass** with required abstract methods:
   - `__bytes__()` - Device protocol serialization
   - `on()` - Turn on with color
   - `color` property - Get/set current color
3. **Define supported_device_ids** with vendor/product ID mappings
4. **Import in vendor's __init__.py** and add to `__all__`
5. **Import in main __init__.py** and add to main `__all__`
6. **Add comprehensive tests** following existing patterns

### Key Design Principles

- **Device-specific classes** enable type safety and plugin discovery
- **Minimal code duplication** (~5-10% is acceptable for hardware abstraction)
- **Clear inheritance hierarchies** with vendor base classes
- **Comprehensive test coverage** with mocked hardware

## Commit Message Format

This project uses conventional commits for automatic changelog generation.
Use these prefixes in your commit messages:

- **feat:** New features and capabilities
- **fix:** Bug fixes and corrections  
- **docs:** Documentation updates
- **refactor:** Code restructuring without behavior changes
- **perf:** Performance improvements
- **test:** Test additions or modifications

**Examples:**
```bash
feat: add support for NewVendor SuperLight device
fix: resolve color parsing issue in Blynclight
docs: update contributing guidelines for new developers
refactor: simplify vendor base class hierarchy
perf: optimize Word.__str__ BitField introspection
test: add comprehensive tests for multi-LED devices
```

**Commit format:**
```
<type>: <description>

[optional body]

[optional footer]
```

## Code Style

### Formatting and Linting

The project uses [ruff][astral-ruff] for code formatting and linting:

- **Line length:** 80 characters for markdown, flexible for code
- **Docstrings:** Sphinx reStructuredText format with single-line summary
- **Type hints:** Required for all public APIs
- **Import sorting:** Automatic via ruff

### Code Conventions

- **Descriptive variable names** that explain purpose, not implementation
- **No comments** - prefer clear code and comprehensive docstrings
- **Exception handling:** Use descriptive variable names (`error` not `e`)
- **Clean exceptions:** Use `contextlib.suppress` instead of `try/except/pass`

### Docstring Format

Use **Sphinx reStructuredText format** focusing on programmer intent rather 
than type information (which is covered by type hints):

```python
def on(self, color: tuple[int, int, int], led: int = 0) -> None:
    """Turn on the light with specified RGB color.

    Sets the device to display the given color immediately. For devices
    with multiple LEDs, use led parameter to target specific LEDs or 
    0 for all LEDs.

    :param color: RGB values from 0-255 for desired color intensity
    :param led: Target LED index, 0 affects all LEDs
    :raises LightUnavailableError: If device communication fails
    """

def get_colors(self) -> list[tuple[int, int, int]]:
    """Get current colors of all LEDs.

    Returns the current color state for each LED in device order.
    Use this to save current state before making temporary changes.

    :return: List of RGB tuples, one per LED in device order
    """
```

**Key principles:**
- **Single-line summary** describing the action or purpose
- **Document programmer intent** - how and why other code should use this
- **Expected inputs** - value ranges, expected content, usage patterns
- **Actions taken** - what happens when called, side effects
- **Exception conditions** - when might this fail and why
- **Return value usage** - how should returned values be used
- **Avoid type redundancy** - type hints handle type information
- **Compact format** - use `:param name: description` rather than verbose sections

## Documentation

### Building Documentation

The project uses MkDocs with the Material theme:

```bash
# Serve locally for development
poe docs-serve

# Build for production
poe docs-build

# Deploy to GitHub Pages (maintainers only)
poe docs-deploy
```

### Writing Documentation

- **API documentation** is auto-generated from docstrings
- **Guides and examples** go in the `docs/` directory
- **Follow 80-column line width** for markdown files
- **Use descriptive headers** and clear examples
- **All Python code blocks are tested** - doc examples must use real
  method names and signatures. Mock infrastructure in `docs/conftest.py`
  handles USB hardware. Run doc tests locally before submitting.

## Releases

### Python Version Configuration

The CI/CD test matrix uses Python versions configured in `pyproject.toml`:

```toml
[tool.busylight_core.ci]
test-python-versions = ["3.11", "3.12", "3.13"]
```

**Benefits:**
- Single source of truth for CI test versions
- Automatic workflow updates when versions change
- Graceful fallback if configuration missing

**Note:** Changing these versions affects all CI/CD testing across the project.

### For Maintainers

Releases are handled through Poe tasks and GitHub Actions:

1. **Create release:**
   ```bash
   poe publish_patch   # 0.1.0 → 0.1.1
   poe publish_minor   # 0.1.1 → 0.2.0
   poe publish_major   # 0.2.0 → 1.0.0
   ```

2. **Automated CI/CD pipeline:**
   - Version bump in pyproject.toml
   - Git commit, tag, and push
   - GitHub Actions: `get-python-versions` → `test` → `build` → [`publish`, `github-release`] → `docs`
   - Parallel execution: PyPI publishing and GitHub release creation run simultaneously
   - Documentation deployment: Only triggered after successful releases
   <!-- add a mermaid diagram here for the ci/cd pipline -->

### Changelog

The CHANGELOG.md is automatically updated using conventional commits:
- **Features** from `feat:` commits
- **Bug Fixes** from `fix:` and `bug:` commits  
- **Documentation** from `docs:` commits
- **Refactoring** from `refactor:` commits
- **Performance** from `perf:` commits

## Getting Help

- **GitHub Discussions:** Ask questions and share ideas
- **Issues:** Report bugs or request features
- **Code Review:** All PRs receive thorough review and feedback

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all
contributors. Please be respectful and constructive in all interactions.

## Questions?

Don't hesitate to ask questions! Create an issue or discussion, and we'll
help you get started. New contributors are always welcome, and we're happy
to provide guidance on getting familiar with the codebase.

<!-- End Links -->

[astral-ruff]: https://docs.astral.sh/ruff
[astral-uv]: https://docs.astral.sh/uv
[direnv]: https://direnv.net/
[good-first-issue]: https://github.com/JnyJny/busylight_core/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22
[help-wanted]: https://github.com/JnyJny/busylight_core/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22
[poe-the-poet]: https://poethepoet.natn.io
[pytest-markdown-docs]: https://github.com/modal-labs/pytest-markdown-docs

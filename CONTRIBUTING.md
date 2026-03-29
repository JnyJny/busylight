# Contributing to BusyLight

Thank you for your interest in contributing! This guide covers the
entire monorepo — both **busylight-for-humans** (CLI & API) and
**busylight-core** (library).

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Git
- USB LED device for testing (optional but recommended)

### Setup

```bash
git clone https://github.com/JnyJny/busylight.git
cd busylight
uv sync --all-groups
```

This is a [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/).
Both packages share a virtual environment. Changes to busylight-core are
immediately available to busylight during development — no reinstall needed.

Optional: if you use [direnv](https://direnv.net/), the included `.envrc`
auto-activates the venv.

### Verify

```bash
uv run pytest packages/busylight-core/tests   # core tests
uv run pytest packages/busylight/tests         # cli/api tests
uv run poe ruff                                # format + lint
```

## Repository Structure

```
busylight/
├── packages/
│   ├── busylight-core/        # Python library (device communication)
│   │   ├── src/busylight_core/
│   │   ├── tests/
│   │   └── docs/
│   └── busylight/             # CLI & HTTP API (user interfaces)
│       ├── src/busylight/
│       ├── tests/
│       └── docs/
├── pyproject.toml             # Workspace root
├── CONTRIBUTING.md            # This file
└── CLAUDE.md                  # AI agent guidance
```

## Development Commands

Both packages use [Poe the Poet](https://poethepoet.natn.io) for task
automation. Run from within a package directory:

### Code Quality

```bash
poe ruff              # format + lint (ruff)
poe test              # run tests (pytest)
poe coverage          # tests with HTML coverage report
```

### busylight-core Specific

```bash
cd packages/busylight-core
poe doc-test          # validate Python code blocks in docs/
poe docs-serve        # serve docs locally
```

### busylight (CLI) Specific

```bash
cd packages/busylight
poe format            # format code
poe check             # lint code
poe clean             # remove build artifacts
```

## Development Workflow

### 1. Issue First

Before starting work:
- Check [existing issues](https://github.com/JnyJny/busylight/issues) for duplicates
- Open an issue to discuss new features or large changes
- Labels: [Good First Issue](https://github.com/JnyJny/busylight/issues?q=is%3Aopen+label%3A%22good+first+issue%22), [Help Wanted](https://github.com/JnyJny/busylight/issues?q=is%3Aopen+label%3A%22help+wanted%22)

### 2. Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 3. Develop

1. Write tests first (TDD encouraged)
2. Implement the change
3. Update documentation if APIs or behavior change
4. Run quality checks before committing

```bash
poe ruff        # format and lint
poe test        # all tests pass
```

### 4. Commit

Use [conventional commits](https://www.conventionalcommits.org/) for
automatic changelog generation:

```bash
feat: add support for NewVendor SuperLight device
fix: resolve color parsing issue in Blynclight
docs: update contributing guidelines
refactor: simplify vendor base class hierarchy
test: add coverage for multi-LED devices
perf: optimize Word.__str__ BitField introspection
```

### 5. Pull Request

1. Push your branch and open a PR
2. Link related issues with `Fixes #123`
3. Wait for CI to pass
4. Address review feedback

## Architecture

### busylight-core (Library)

The device communication layer:

- **Light** (`light.py`) — Abstract base class for all devices
- **Hardware** (`hardware.py`) — Device detection and connection
- **Vendors** (`vendors/`) — Device-specific implementations (one subpackage per vendor)
- **Mixins** — `ColorableMixin` (color management), `TaskableMixin` (async effects)

Device discovery uses `abc.ABC.__subclasses__()` — every `Light` subclass
is automatically discoverable.

**Key rule: DO NOT consolidate vendor classes.** Each device gets its own
class. This preserves plugin discovery and type safety.

### busylight (CLI & API)

The user-facing layer built on busylight-core:

- **CLI** (`src/busylight/`) — Typer-based command-line interface
- **Effects** (`effects/`) — Steady, Blink, Spectrum, Gradient
- **Controller** (`controller.py`) — Multi-device coordination
- **Web API** (`api/`) — FastAPI with Pydantic models

### Adding Device Support

New device support goes in **busylight-core**:

1. Create or use existing vendor package in `src/busylight_core/vendors/`
2. Implement `Light` subclass with required abstract methods:
   - `__bytes__()` — device protocol serialization
   - `on()` — turn on with color
   - `color` property — get/set current color
3. Define `supported_device_ids` with vendor/product ID mappings
4. Import in vendor `__init__.py` and main `__init__.py`
5. Add comprehensive tests following existing patterns

Three device patterns exist: simple (ColorableMixin only), complex
(Word/BitField protocol), and multi-LED (array targeting). Follow
whichever matches your device.

### Adding Effects

New effects go in **busylight**:

1. Inherit from `BaseEffect` in `effects/effect.py`
2. Implement `colors` property (list of RGB tuples) and `default_interval`
3. Add to `effects/__init__.py`
4. Effects are automatically available via CLI discovery

## Testing

### Test Structure

- Tests live in each package's `tests/` directory
- Mock hardware — tests should never require real devices
- `vendor_examples/` provides reusable test data for core

### Running Tests

```bash
# All tests for one package
uv run pytest packages/busylight-core/tests
uv run pytest packages/busylight/tests

# Specific file or pattern
uv run pytest packages/busylight-core/tests/test_light.py
uv run pytest -k "blynclight"

# With coverage
cd packages/busylight-core && poe coverage
```

### Doc Tests (busylight-core)

All Python code blocks in `docs/` are tested via pytest-markdown-docs.
Mock USB hardware lives in `docs/conftest.py`.

- Use `` ```python continuation `` for blocks that depend on prior imports
- Use `` ```python notest `` to exclude a block
- If you change a public API, update doc examples — CI catches mismatches

## Code Style

### Formatting and Linting

[Ruff](https://docs.astral.sh/ruff/) handles formatting and linting.
Run `poe ruff` before committing.

### Conventions

- **Type hints** on all public APIs
- **Docstrings** in Sphinx reStructuredText format, focused on intent:
  ```python
  def on(self, color: tuple[int, int, int], led: int = 0) -> None:
      """Turn on the light with specified RGB color.

      :param color: RGB values from 0-255 for desired color intensity
      :param led: Target LED index, 0 affects all LEDs
      :raises LightUnavailableError: If device communication fails
      """
  ```
- **No inline comments** — prefer clear code and docstrings
- **Descriptive names** — explain purpose, not implementation
- **Clean exceptions** — use `contextlib.suppress` over bare `try/except/pass`

## Platform Notes

- **macOS** — works out of the box
- **Linux** — requires udev rules for USB access (`busylight udev-rules`)
- **Windows** — may work, untested, patches welcome

## Releases (Maintainers)

Each package releases independently:

```bash
cd packages/busylight-core
poe publish_patch    # 2.2.0 → 2.2.1

cd packages/busylight
poe publish          # bumps, builds, publishes
```

CI/CD pipeline: version bump → test → build → publish to PyPI + GitHub
release → deploy docs. Changelogs are auto-generated from conventional
commits via [git-cliff](https://git-cliff.org/).

## Getting Help

- [GitHub Issues](https://github.com/JnyJny/busylight/issues) — bugs and feature requests
- [GitHub Discussions](https://github.com/JnyJny/busylight/discussions) — questions and ideas
- [Device Support Requests](https://github.com/JnyJny/busylight/issues/new) — new hardware

We're happy to help new contributors get started.

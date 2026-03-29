# CLAUDE.md

Monorepo for controlling USB status lights from Python. Two packages in `packages/`.

## Workspace

This is a [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/).
Both packages share a virtual environment. Run `uv sync` from root.

## Packages

### busylight-core (`packages/busylight-core/`)

Python library for device communication. Plugin architecture, multi-vendor.

**Key files:**
- `src/busylight_core/light.py` — Base class for all devices
- `src/busylight_core/hardware.py` — Device connection handling
- `src/busylight_core/vendors/` — Device-specific implementations
- `src/busylight_core/mixins/` — ColorableMixin, TaskableMixin

### busylight (`packages/busylight/`)

CLI and HTTP API built on busylight-core.

**Key files:**
- `src/busylight/__main__.py` — CLI entry point
- `src/busylight/effects/` — Steady, Blink, Spectrum, Gradient
- `src/busylight/controller.py` — Multi-device coordination
- `src/busylight/api/` — FastAPI web server

## Commands

Run from package directories:

```bash
# busylight-core
cd packages/busylight-core
poe test              # unit tests
poe doc-test          # validate code blocks in docs/
poe ruff              # format + lint
poe coverage          # coverage report
poe docs-serve        # serve docs locally

# busylight (CLI)
cd packages/busylight
poe test              # unit tests
poe ruff              # format + lint (check + format)
poe coverage          # coverage report
```

## Architecture Rules

**DO NOT consolidate vendor classes.** Each device gets its own class in
`vendors/`. This preserves plugin discovery via `abc.ABC.__subclasses__()`
and type safety.

**Three device patterns:**
- Simple: ColorableMixin only
- Complex: Word/BitField protocol (Embrava, Kuando, etc.)
- Multi-LED: Array targeting (BlinkStick, Luxafor Flag)

Preserve these patterns. Don't merge them.

### TaskableMixin

Automatic strategy selection:
- **Asyncio context:** Uses `asyncio.Task`
- **Non-asyncio context:** Uses `threading.Timer`
- No user configuration needed

## Adding Devices

Goes in busylight-core:

1. Create vendor package in `vendors/` if needed
2. Implement `Light` subclass (`__bytes__`, `on`, `color` property)
3. Define `supported_device_ids`
4. Import in vendor `__init__.py` and main `__init__.py`
5. Add tests in `tests/`

## Doc Tests

All Python code blocks in `packages/busylight-core/docs/` are tested
via pytest-markdown-docs. Mock hardware in `docs/conftest.py`.

- `continuation` marker for blocks depending on prior imports
- `notest` marker to exclude blocks
- **If you change a public API, update doc examples** — CI catches mismatches

## Code Style

- **Ruff** for formatting and linting — run `poe ruff` before commits
- **Type hints** on all public APIs
- **Docstrings:** Sphinx format, focus on programmer intent:
  ```python
  def on(self, color: tuple[int, int, int], led: int = 0) -> None:
      """Turn on the light with specified RGB color.

      :param color: RGB values from 0-255
      :param led: Target LED index, 0 for all
      """
  ```
- No inline comments — prefer clear code and docstrings

## Release Pipeline

Per-package releases. Pipeline:
`get-python-versions` → `test` → `build` → [`publish`, `github-release`] → `docs`

Python test versions configured in each package's `pyproject.toml`:
```toml
[tool.busylight_core.ci]
test-python-versions = ["3.11", "3.12", "3.13"]
```

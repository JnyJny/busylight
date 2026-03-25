# CLAUDE.md

Guidance for Claude Code when working with this repository.

## Overview

User interfaces for USB LED lights via [busylight-core][busylight-core].
Core handles device communication; this provides CLI and HTTP API.

## Development Commands

### Setup
```bash
python3 -m pip install uv
uv venv .venv && source .venv/bin/activate && uv sync --all-extras
```

### Testing
```bash
pytest                           # all tests
poe coverage                     # tests with coverage + open report
pytest tests/test_manager.py     # specific file
```

### Code Quality
```bash
poe format                       # format code
poe check                        # lint code
poe ruff                         # check + format
```

### Build & Release
```bash
uv build                         # build package
poe clean                        # clean artifacts
poe requirements                 # update requirements.txt
poe publish                      # patch version + publish
```

### Scripts
- `busylight` - CLI for controlling lights
- `busyserve` - Web API server

## Architecture

Interface layer for [busylight-core][busylight-core] (handles device I/O).

### Components

#### Core Integration
`busylight-core` handles device discovery, USB/Serial communication, vendor protocols

#### Interfaces
CLI (`busylight`) and HTTP API (`busyserve`) 

#### Effects
Steady, Blink, Spectrum, Gradient

#### Manager
`LightManager` coordinates multiple lights, async tasks, batching

#### Web API
FastAPI + Pydantic in `api/`

### Patterns
- Facade/Adapter for busylight-core
- Async effects for non-blocking operation

### Platform
- macOS/Linux (primary), Windows (untested)
- Linux needs udev rules

### Config
- `pyproject.toml` + `uv`
- Core: `busylight-core`
- Optional: `webapi` group
- Colors: RGB tuples, named colors, hex

[busylight-core]: https://github.com/JnyJny/busylight-core
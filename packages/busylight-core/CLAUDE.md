# CLAUDE.md

Python library for controlling USB status lights from various vendors using a plugin architecture.

## Commands
- `poe test` - Run unit tests
- `poe doc-test` - Run doc tests (validates Python code blocks in docs/)
- `poe ruff` - Format and lint
- `poe coverage` - Coverage report
- `poe docs-serve` - Serve docs locally

## Architecture
- **Light** (src/busylight_core/light.py) - Base class for all devices
- **Hardware** (src/busylight_core/hardware.py) - Device connection handling
- **Vendors** (src/busylight_core/vendors/) - Device-specific implementations
- **Mixins** - ColorableMixin, TaskableMixin for shared functionality

### TaskableMixin
Provides automatic task management with environment-driven strategy selection:
- **Asyncio context**: Uses `asyncio.Task` for periodic execution
- **Non-asyncio context**: Uses `threading.Timer` for periodic execution
- **Automatic detection**: No user configuration required
- **Backward compatibility**: Maintains existing coroutine-based API

### Adding Devices
1. Create vendor package in vendors/ if needed  
2. Implement Light subclass
3. Import in vendor __init__.py and main __init__.py
4. Discovery uses abc.ABC.__subclasses__()

## Release Workflow
Pipeline: `get-python-versions` → `test` → `build` → [`publish`, `github-release`] → `docs`

- **Python versions**: Configure test matrix in `[tool.busylight_core.ci].test-python-versions`
- **Artifact caching**: Package built once, reused by publish/release jobs
- **Parallel execution**: Publish and GitHub release run simultaneously  
- **Docs deployment**: Triggered only after successful releases

## Code Guidelines

**Architecture**: **DO NOT** consolidate vendor classes - this breaks plugin discovery and type safety.

**Docstrings**: Use Sphinx format focusing on programmer intent:
```python
def method(self, param: str) -> bool:
    """Brief summary.
    
    :param param: What user provides
    :return: How to use result
    """
```

**Patterns**: Three device types - simple (ColorableMixin), complex (Word/BitField), multi-LED (arrays). Preserve these patterns.

**Quality**: Run `poe ruff` before commits.

## Doc Tests
All Python code blocks in `docs/` are tested via pytest-markdown-docs.
Mock USB hardware lives in `docs/conftest.py`. If you change any public API,
update the doc examples -- CI will catch mismatches. Use `continuation` marker
for blocks that depend on prior imports, `notest` for untestable blocks.
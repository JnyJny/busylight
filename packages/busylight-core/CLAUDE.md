# CLAUDE.md

See [root CLAUDE.md](../../CLAUDE.md) for workspace-level guidance.

## busylight-core Quick Reference

Python library for USB status light control. Plugin architecture.

### Commands

```bash
poe test          # unit tests
poe doc-test      # validate code blocks in docs/
poe ruff          # format + lint
poe coverage      # coverage report
poe docs-serve    # serve docs locally
```

### Key Rules

- **DO NOT consolidate vendor classes** — breaks plugin discovery
- Three device patterns: simple, complex (Word/BitField), multi-LED
- Doc tests run on all Python blocks in `docs/` — update examples when changing APIs
- Mock hardware in `docs/conftest.py`
- `continuation` marker for doc-test blocks depending on prior imports
- `notest` marker to exclude a block from doc-testing

### Adding Devices

1. Create vendor package in `vendors/` if needed
2. Implement `Light` subclass (`__bytes__`, `on`, `color` property)
3. Define `supported_device_ids`
4. Import in vendor `__init__.py` and main `__init__.py`
5. Add tests in `tests/`

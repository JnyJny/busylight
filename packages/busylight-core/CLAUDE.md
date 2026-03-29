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

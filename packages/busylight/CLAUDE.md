# CLAUDE.md

See [root CLAUDE.md](../../CLAUDE.md) for workspace-level guidance.

## busylight Quick Reference

CLI and HTTP API for USB LED lights, built on busylight-core.

### Commands

```bash
poe test          # unit tests
poe ruff          # format + lint (check + format)
poe coverage      # coverage report
poe format        # format only
poe check         # lint only
poe clean         # remove build artifacts
```

### Entry Points

- `busylight` — CLI for controlling lights
- `busyserve` — Web API server (requires `[webapi]` extra)

### Architecture

- Effects in `effects/` — inherit from `BaseEffect`
- API in `api/` — FastAPI + Pydantic
- Device communication delegated entirely to busylight-core

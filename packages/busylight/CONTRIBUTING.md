# Contributing to BusyLight for Humans

See the [root contributing guide](../../CONTRIBUTING.md) for development
setup, workflow, code style, and commit conventions.

## Package-Specific Notes

### Effects Development

New effects inherit from `BaseEffect` in `effects/effect.py`:
- Implement `colors` property (list of RGB tuples)
- Implement `default_interval` property
- Add to `effects/__init__.py`
- Effects are automatically discoverable via CLI

See `effects/blink.py` or `effects/spectrum.py` for examples.

### Web API

The HTTP API uses FastAPI with Pydantic models in `src/busylight/api/`.
Install with the webapi extra: `pip install busylight-for-humans[webapi]`

### Hardware Support

Device support is handled in
[busylight-core](../busylight-core/CONTRIBUTING.md). This package
consumes busylight-core's device abstraction — you shouldn't need to
touch device-level code here.

### Releases

```bash
poe publish          # bumps version, builds, publishes
```

Issues: https://github.com/JnyJny/busylight/issues

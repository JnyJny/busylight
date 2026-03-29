# Contributing to busylight-core

See the [root contributing guide](../../CONTRIBUTING.md) for development
setup, workflow, code style, and commit conventions.

## Package-Specific Notes

### Adding Device Support

This is the most common contribution to busylight-core. See the
[Architecture > Adding Device Support](../../CONTRIBUTING.md#adding-device-support)
section in the root guide.

Quick checklist:
1. Vendor package in `src/busylight_core/vendors/`
2. `Light` subclass with `__bytes__`, `on`, `color`
3. `supported_device_ids` tuple
4. Imports in `__init__.py` files
5. Tests in `tests/`
6. Doc examples if adding new public API

### Doc Tests

All Python code blocks in `docs/` are tested automatically. If you
change a public API, update the doc examples. Mock hardware lives
in `docs/conftest.py`. See the root guide for marker details.

### Releases

```bash
poe publish_patch    # 2.2.0 → 2.2.1
poe publish_minor    # 2.2.0 → 2.3.0
poe publish_major    # 2.2.0 → 3.0.0
```

Issues: https://github.com/JnyJny/busylight/issues

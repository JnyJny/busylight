"""Test configuration and shared fixtures."""

import gc

import pytest

from busylight_core.light import Light


@pytest.fixture(autouse=True, scope="session")
def turn_off_lights_after_tests() -> None:
    """Turn off all connected lights after the test session completes.

    Finds any Light instances left open by tests and turns them off
    before releasing their hardware handles.
    """
    yield  # type: ignore[misc]

    gc.collect()
    for obj in gc.get_objects():
        try:
            if isinstance(obj, Light) and obj.hardware.is_acquired:
                obj.off()
                obj.release()
        except Exception:  # noqa: S110
            pass

"""Test version attribute availability."""

import busylight_core


def test_version_exists() -> None:
    """Test that version attribute exists."""
    assert hasattr(busylight_core, "version")


def test_version_is_string() -> None:
    """Test that version attribute is a string."""
    assert isinstance(busylight_core.version, str)

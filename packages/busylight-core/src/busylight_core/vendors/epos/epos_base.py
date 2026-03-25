"""EPOS vendor base class."""

from busylight_core.light import Light


class EPOSBase(Light):
    """Base class for EPOS devices.

    Provides common functionality for all EPOS devices,
    primarily the Busylight product line.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for EPOS devices."""
        return "EPOS"

"""Embrava vendor base class."""

from busylight_core.light import Light


class EmbravaBase(Light):
    """Base class for all Embrava devices.

    Provides the vendor identifier shared by all Embrava product lines.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for Embrava devices."""
        return "Embrava"

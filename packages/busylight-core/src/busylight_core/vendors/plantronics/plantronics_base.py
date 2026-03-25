"""Plantronics vendor base class."""

from busylight_core.vendors.embrava.blynclight_plus import BlynclightPlus


class PlantronicsBase(BlynclightPlus):
    """Base class for Plantronics devices with audio capabilities.

    Plantronics devices are typically OEM versions of Embrava BlynclightPlus
    devices with full audio and visual functionality but different vendor branding.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for Plantronics devices."""
        return "Plantronics"

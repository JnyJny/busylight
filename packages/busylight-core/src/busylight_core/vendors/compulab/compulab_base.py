"""CompuLab vendor base class."""

from busylight_core.light import Light


class CompuLabBase(Light):
    """Base class for CompuLab devices.

    Provides common functionality for all CompuLab devices,
    primarily the fit-statUSB product line. Use this as a base
    class when implementing new CompuLab device variants.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for CompuLab devices.

        Provides the official vendor branding for user interfaces
        and device identification.

        :return: Official vendor name string
        """
        return "CompuLab"

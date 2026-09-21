"""VT vendor base class."""

from busylight_core.light import Light


class VTBase(Light):
    """Base class for VT Busylight devices.

    Provides common functionality for all VT devices,
    primarily the DND product line. Use this as a base
    class when implementing DND variants.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for VT devices.

        Provides the official vendor branding for user interfaces
        and device identification.

        :return: Official vendor name string
        """
        return "VT"

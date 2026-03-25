"""Kuando vendor base class."""

from busylight_core.light import Light


class KuandoBase(Light):
    """Base class for Kuando Busylight devices.

    Provides common functionality for all Kuando devices,
    primarily the Busylight product line. Use this as a base
    class when implementing new Kuando device variants.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for Kuando devices.

        Provides the official vendor branding for user interfaces
        and device identification.

        :return: Official vendor name string
        """
        return "Kuando"

"""Agile Innovative vendor base class."""

from busylight_core.light import Light


class AgileInnovativeBase(Light):
    """Base class for Agile Innovative BlinkStick devices.

    Provides common functionality for all Agile Innovative devices,
    primarily the BlinkStick product line. Use this as a base class
    when implementing new BlinkStick variants or related devices.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for Agile Innovative devices.

        Provides the official vendor branding for user interfaces
        and device identification.

        :return: Official vendor name string
        """
        return "Agile Innovative"

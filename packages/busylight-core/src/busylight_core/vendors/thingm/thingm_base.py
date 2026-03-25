"""ThingM vendor base class."""

from busylight_core.light import Light


class ThingMBase(Light):
    """Base class for ThingM Blink(1) devices.

    Provides common functionality for all ThingM devices,
    primarily the Blink(1) product line. Use this as a base
    class when implementing new Blink(1) variants.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for ThingM devices.

        Provides the official vendor branding for user interfaces
        and device identification.

        :return: Official vendor name string
        """
        return "ThingM"

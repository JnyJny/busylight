"""Luxafor vendor base class."""

from loguru import logger

from busylight_core.hardware import Hardware
from busylight_core.light import Light


class LuxaforBase(Light):
    """Base class for Luxafor USB status light devices.

    Provides common functionality for all Luxafor devices including
    the Flag, Mute, Orb, Bluetooth, and BusyTag product lines.
    Use this as a base class when implementing new Luxafor device
    variants that share the core USB protocol and feature set.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for Luxafor devices.

        Provides the official vendor branding for user interfaces
        and device identification.

        :return: Official vendor name string
        """
        return "Luxafor"

    @classmethod
    def claims(cls, hardware: Hardware, product_check: bool = True) -> bool:
        """Check if hardware is a compatible Luxafor device.

        Performs enhanced device identification by checking both the USB
        vendor/product ID and the product name string. Use product_check=False
        to bypass product name verification for devices like BusyTag that
        may have inconsistent product strings.

        :param hardware: Hardware instance to test for compatibility
        :param product_check: Whether to verify product name string matches
        :return: True if hardware is a supported Luxafor device
        """
        result = super().claims(hardware)

        if not product_check:
            return result

        if not result:
            return False

        try:
            product = hardware.product_string.split()[-1].casefold()
        except (KeyError, IndexError) as error:
            logger.debug(f"problem {error} processing product_string for {hardware}")
            return False

        return product in [
            value.casefold() for value in cls.supported_device_ids.values()
        ]

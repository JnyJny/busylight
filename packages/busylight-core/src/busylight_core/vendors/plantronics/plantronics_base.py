"""Plantronics vendor base class."""

from busylight_core.light import Light
from busylight_core.vendors.embrava.blynclight_protocol import BlynclightPlusProtocol


class PlantronicsBase(BlynclightPlusProtocol, Light):
    """Base class for Plantronics devices.

    Plantronics status lights are OEM versions of Embrava Blynclight
    devices -- same USB packet format, same state machine, same
    sound/flash/dim capabilities. The BlynclightProtocol mixin
    provides the protocol implementation without inheriting Embrava's
    vendor hierarchy.

    This keeps the class tree clean: PlantronicsBase is a Light, not
    an EmbravaBase. Vendor-scoped queries like
    EmbravaLights.available_hardware() won't return Plantronics
    devices, and Plantronics devices won't inherit Embrava's
    supported_device_ids.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for Plantronics devices."""
        return "Plantronics"

"""Utility functions for generating hardware examples.

This module provides helper functions for creating mock hardware definitions
used in testing vendor-specific busylight devices.
"""

from busylight_core import Light
from busylight_core.hardware import ConnectionType, Hardware


def make_hardware(
    subclass: Light,
    template: dict[str, str | bytes | int],
) -> list[Hardware]:
    """Generate mock hardware instances for a given Light subclass.

    Args:
        subclass: The Light subclass to generate hardware for
        template: A dictionary template containing hardware properties

    Yields:
        Hardware instances for each supported device ID of the subclass

    """
    for v, p in subclass.supported_device_ids:
        match template.get("device_type", ConnectionType.HID):
            case ConnectionType.HID:
                yield Hardware.from_hid({**template, "vendor_id": v, "product_id": p})
            case ConnectionType.SERIAL:
                yield Hardware(**{**template, "vendor_id": v, "product_id": p})

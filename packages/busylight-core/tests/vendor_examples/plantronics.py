"""Hardware examples for Plantronics busylight devices.

This module provides mock hardware definitions for testing Plantronics
busylight devices, including the Status Indicator product line.
"""

from busylight_core.vendors.plantronics import StatusIndicator

from .utils import make_hardware

status_indicator_template = {
    "path": b"/BOGUS/PATH",
    "serial_number": "",
    "release_number": 1,
    "manufacturer_string": "",
    "product_string": "Plantronics Status Indicator",
    "usage_page": 65280,
    "usage": 1,
    "interface_number": 0,
    "bus_type": 1,
}

PLANTRONICS_HARDWARE = {
    StatusIndicator: make_hardware(StatusIndicator, status_indicator_template),
}

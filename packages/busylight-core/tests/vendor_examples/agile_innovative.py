"""Hardware examples for Agile Innovative busylight devices.

This module provides mock hardware definitions for testing Agile Innovative
busylight devices, including the BlinkStick product line.
"""

from busylight_core.vendors.agile_innovative import BlinkStickSquare

from .utils import make_hardware

blinkstick_square_template = {
    "path": b"/BOGUS/PATH",
    "serial_number": "BS032974-3.0",
    "release_number": 512,
    "manufacturer_string": "Agile Innovative Ltd",
    "product_string": "BlinkStick",
    "usage_page": 65280,
    "usage": 1,
    "interface_number": 0,
    "bus_type": 1,
}

AGILE_INNOVATIVE_HARDWARE = {
    BlinkStickSquare: make_hardware(BlinkStickSquare, blinkstick_square_template),
}

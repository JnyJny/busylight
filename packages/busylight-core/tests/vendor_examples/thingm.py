"""Hardware examples for ThingM busylight devices.

This module provides mock hardware definitions for testing ThingM
busylight devices, including the Blink1 product line.
"""

from busylight_core.vendors.thingm import Blink1

from .utils import make_hardware

blink1_template = {
    "path": b"/BOGUS/PATH",
    "serial_number": "3684ee30",
    "release_number": 257,
    "manufacturer_string": "ThingM",
    "product_string": "blink(1) mk3",
    "usage_page": 65451,
    "usage": 8192,
    "interface_number": 0,
    "bus_type": 1,
}


THINGM_HARDWARE = {
    Blink1: make_hardware(Blink1, blink1_template),
}

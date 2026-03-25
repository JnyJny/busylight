"""Hardware examples for Kuando busylight devices.

This module provides mock hardware definitions for testing Kuando
busylight devices, including the Busylight Alpha and Omega product lines.
"""

from busylight_core.vendors.kuando import BusylightAlpha, BusylightOmega

from .utils import make_hardware

busylight_alpha_template = {
    "path": b"/BOGUS/PATH",
    "serial_number": "",
    "release_number": 256,
    "manufacturer_string": "PLENOM APS",
    "product_string": "BUSYLIGHT ALPHA",
    "usage_page": 65280,
    "usage": 1,
    "interface_number": 0,
    "bus_type": 1,
}

busylight_omega_template = {
    "path": b"/BOGUS/PATH",
    "serial_number": "",
    "release_number": 256,
    "manufacturer_string": "PLENOM APS",
    "product_string": "BUSYLIGHT OMEGA",
    "usage_page": 65280,
    "usage": 1,
    "interface_number": 0,
    "bus_type": 1,
}

KUANDO_HARDWARE = {
    BusylightAlpha: make_hardware(BusylightAlpha, busylight_alpha_template),
    BusylightOmega: make_hardware(BusylightOmega, busylight_omega_template),
}

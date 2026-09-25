"""Hardware examples for VT DND devices.

This module provides mock hardware definitions for testing VT
DND devices, including the DND Alpha and Omega product lines.
"""

from busylight_core.vendors.vt import DNDAlpha, DNDOmega

from .utils import make_hardware

dnd_alpha_template = {
    "path": b"/BOGUS/PATH",
    "serial_number": "",
    "release_number": 256,
    "manufacturer_string": "VT",
    "product_string": "DND Alpha",
    "usage_page": 65280,
    "usage": 1,
    "interface_number": 0,
    "bus_type": 1,
}

dnd_omega_template = {
    **dnd_alpha_template,
    "product_string": "DND Omega",
}

VT_HARDWARE = {
    DNDAlpha: make_hardware(DNDAlpha, dnd_alpha_template),
    DNDOmega: make_hardware(DNDOmega, dnd_omega_template),
}

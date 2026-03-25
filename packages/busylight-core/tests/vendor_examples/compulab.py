"""Hardware examples for Compulab busylight devices.

This module provides mock hardware definitions for testing Compulab
busylight devices, including the fit-StatUSB product line.
"""

from busylight_core.hardware import ConnectionType
from busylight_core.vendors.compulab import FitStatUSB

from .utils import make_hardware

fit_statusb_template = {
    "device_type": ConnectionType.SERIAL,
    "path": b"/BOGUS/PATH",
    "serial_number": "193F914722000800",
    "manufacturer_string": "Compulab LTD",
    "product_string": "fit_StatUSB",
    "bus_type": 1,
}


COMPULAB_HARDWARE = {
    FitStatUSB: make_hardware(FitStatUSB, fit_statusb_template),
}

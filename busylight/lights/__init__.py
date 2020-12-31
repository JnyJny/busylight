"""USB Connected Presence Lights
"""


from typing import Dict, List, Union

import hid

## Developer: How To Add Support for a New Light
##
## 0. Create a new light class subclassed from busylight.light.USBLIght
##    - implement 'on', 'off', 'blink' methods at a minimum
##    - define class attribute list VENDOR_IDS
##    - define class attribute list PRODUCT_IDS
##    - define class asttribute string vendor
##
## 1. Import the module for the new light here in this file.


from .usblight import USBLight
from .exceptions import USBLightNotFound
from .exceptions import USBLightUnknownVendor
from .exceptions import USBLightUnknownProduct
from .exceptions import USBLightInUse
from .exceptions import USBLightIOError

# EJO some kind of cool dynamic import would be sweet right here

from .agile_innovations import BlinkStick
from .embrava import Blynclight
from .kuando import BusyLight
from .luxafor import Flag
from .thingm import Blink1

__all__ = [
    "USBLight",
    "USBLightNotFound",
    "USBLightUnknownVendor",
    "USBLightUnknownProduct",
    "USBLightInUse",
    "USBLightIOError",
]

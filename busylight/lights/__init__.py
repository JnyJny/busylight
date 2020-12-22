"""USB Connected Presence Lights
"""


from typing import Dict, List, Union

import hid

## Developer: How To Add Support for a New Light
##
## 0. Create a new light class subclassed from busylight.light.USBLIght
##    - implement 'on', 'off', 'blink' methods at a minimum
##    - define class attribute list VENDOR_IDS
##    - define class asttribute string __vendor__
##
##    Use the existing light subclasses as inspiration.
##
## 1. Import the module for the new light here in this file.
## 2. Add the new class to the SUPPORTED_LIGHTS list
## 3. Add the name of the new class to the __all__ list


from .usblight import USBLight
from .exceptions import USBLightNotFound
from .exceptions import USBLightUnknownVendor
from .exceptions import USBLightUnknownProduct
from .exceptions import USBLightInUse
from .exceptions import USBLightIOError

from .agile_innovations import BlinkStick
from .embrava import Blynclight
from .kuando import BusyLight
from .luxafor import Flag
from .thingm import Blink1

SUPPORTED_LIGHTS = USBLight.supported_lights()

KNOWN_VENDOR_IDS = sum([l.VENDOR_IDS for l in SUPPORTED_LIGHTS], [])

__all__ = [
    "KNOWN_VENDOR_IDS",
    "SUPPORTED_LIGHTS",
    "USBLight",
    "USBLightNotFound",
    "USBLightUnknownVendor",
    "USBLightUnknownProduct",
    "USBLightInUse",
    "USBLightIOError",
]

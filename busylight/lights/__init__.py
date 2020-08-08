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


from .agile_innovations import BlinkStick
from .embrava import Blynclight
from .kuando import BusyLight
from .luxafor import Flag
from .thingm import Blink1

from .usblight import USBLight
from .usblight import UnknownUSBLight
from .usblight import USBLightInUse
from .usblight import USBLightIOError
from .usblight import USBLightNotFound

SUPPORTED_LIGHTS = [BlinkStick, Blynclight, Blink1, BusyLight, Flag]

KNOWN_VENDOR_IDS = sum([l.VENDOR_IDS for l in SUPPORTED_LIGHTS], [])

__all__ = [
    "Blink1",
    "Blynclight",
    "BusyLight",
    "Flag",
    "KNOWN_VENDOR_IDS",
    "SUPPORTED_LIGHTS",
    "UnknownUSBLight",
    "USBLight",
    "USBLightInUse",
    "USBLightIOError",
    "USBLightNotFound",
]

"""USB Connected Presence Lights
"""


from typing import Dict, List, Union

import hid

from .usblight import UnknownUSBLight, USBLightInUse

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


from .blynclight import BlyncLight
from .kuando import BusyLight
from .luxafor import Flag
from .thingm import Blink1

SUPPORTED_LIGHTS = [BlyncLight, Blink1, BusyLight, Flag]

KNOWN_VENDOR_IDS = sum([l.VENDOR_IDS for l in SUPPORTED_LIGHTS], [])


def available_lights(vendor_ids: List[int] = None) -> List[Dict[str, Union[int, str]]]:
    """Returns a list of dictionaries, each dictionary describing an available USB
    attached LED light. 

    The available list can be filtered by an optionally supplied list of 16-bit USB
    vendor_ids. Otherwise the list is filtered by devices known to this package (see
    the lists SUPPORTED_LIGHTS and KNOWN_VENDOR_IDS in this module).

    :param vendor_ids: int
    :return: List[Dict[str, Union[int, str]]]
    """

    vendor_ids = vendor_ids or KNOWN_VENDOR_IDS

    lights = []
    for vendor_id in vendor_ids:
        lights.extend(hid.enumerate(vendor_id))
    return lights


def get_light(index: int = 0) -> object:
    """Returns a USBLight subclass that has been initialized and opened.

    :param index: int
    :return: busylight.light.USBLight subclass
    """

    try:
        info = available_lights()[index]
    except IndexError:
        raise Exception("No light available with id '{index}'")

    for LightClass in SUPPORTED_LIGHTS:
        try:
            return LightClass.from_dict(info)
        except UnknownUSBLight:
            pass
    else:
        raise Exception("Did not find known light.", info)


def get_all_lights() -> object:
    """Generator function yields a light for each available light found
    initalized and opened.

    :return: USBLight subclass
    """

    for info in available_lights():
        for LightClass in SUPPORTED_LIGHTS:
            try:
                yield LightClass.from_dict(info)
            except UnknownUSBLight:
                pass
            except USBLightInUse:
                pass


__all__ = [
    "Blink1",
    "BlyncLight",
    "BusyLight",
    "Flag",
    "available_lights",
    "get_light",
    "get_all_lights",
]

"""
"""


from typing import Dict, List, Union

import hid

from .usblight import UnknownUSBLight

## To add a new light, create a new light class subclassed from
## usblight.USBLight and import it here.
##
## from .coolnewlight import CoolNewLight
##
## Added it to the SUPPORTED_LIGHTS list and you are done (provided you have
## implemented the on, off and blink methods in your CoolNewLight). Also
## make sure CoolNewLight defines a list class attribute named VENDOR_IDS
## and string class attribute named __vendor__.

from .blynclight import BlyncLight
from .luxafor import Flag

SUPPORTED_LIGHTS = [BlyncLight, Flag]

KNOWN_VENDOR_IDS = sum([l.VENDOR_IDS for l in SUPPORTED_LIGHTS], [])


def available_lights(vendor_ids: List[int] = None) -> List[Dict[str, Union[int, str]]]:
    """Returns a list of dictionaries, each dictionary describing an available USB
    attached LED light. 

    The available list can be filtered by an optionally supplied list of 16-bit USB
    vendor_ids. Otherwise the list is filtered by devices known to this package (see
    SUPPORTED_LIGHTS and KNOWN_VENDOR_IDS).

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
        raise Exception("No lights detected")

    for LightClass in SUPPORTED_LIGHTS:
        try:
            return LightClass.from_dict(info)
        except UnknownUSBLight:
            pass
    else:
        raise Exception("Did not find known light.")


def get_all_lights() -> object:
    """Generator function yields a light for each available light found
    initalized and opened.

    :return: USBLight subclass
    """

    lights = []
    for info in available_lights():
        for LightClass in SUPPORTED_LIGHTS:
            try:
                yield LightClass.from_dict(info)
            except UnknownUSBLight:
                pass


__all__ = ["BlyncLight", "Flag", "available_lights", "get_light", "get_all_lights"]

""" Supported USB-attached Lights
"""

from .exceptions import (
    InvalidHidInfo,
    LightNotFound,
    LightUnavailable,
    LightUnsupported,
    NoLightsFound,
)

from .usblight import USBLight

from .hidinfo import HidInfo

from .speed import Speed

# import new light subclasses here
from .agile_innovative import BlinkStick
from .embrava import Blynclight
from .kuando import Busylight
from .luxafor import Flag, Mute, Orb
from .plantronics import Status_Indicator
from .thingm import Blink1


# also include new light subclasses here
__all__ = [
    "Blink1",
    "BlinkStick",
    "Blynclight",
    "Busylight",
    "Flag",
    "HidInfo",
    "InvalidHidInfo",
    "LightNotFound",
    "LightUnavailable",
    "LightUnsupported",
    "Mute",
    "NoLightsFound",
    "Orb",
    "Speed",
    "Status_Indicator",
    "USBLight",
]

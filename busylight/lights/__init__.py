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
from .usblight import HidInfo

from .color import ColorTuple, ColorList, parse_color
from .speed import Speed

from .effects import Effects
from .effects import FrameTuple, FrameGenerator

# import new light subclasses here
from .agile_innovative import BlinkStick
from .embrava import Blynclight
from .kuando import Busylight
from .luxafor import Flag, Mute, Orb
from .plantronics import Status_Indicator
from .thingm import Blink1


# include new light subclasses here
__all__ = [
    "Blink1",
    "BlinkStick",
    "Blynclight",
    "Busylight",
    "ColorTuple",
    "ColorList",
    "Effects",
    "Flag",
    "FrameGenerator",
    "FrameTuple",
    "HidInfo",
    "InvalidHidInfo",
    "LightNotFound",
    "LightUnavailable",
    "LightUnsupported",
    "Mute",
    "NoLightsFound",
    "Orb",
    "parse_color",
    "Speed",
    "Status_Indicator",
    "USBLight",
]

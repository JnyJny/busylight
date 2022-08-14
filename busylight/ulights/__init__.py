""" Support for USB Connected Lights

"""

from .light import Light
from .hidlight import HIDLight
from .seriallight import SerialLight

from .exceptions import (
    InvalidLightInfo,
    LightNotFound,
    LightUnavailable,
    LightUnsupported,
    NoLightsFound,
)

from .agile_innovative import BlinkStick
from .compulab import Fit_StatUSB
from .embrava import Blynclight
from .kuando import Busylight
from .luxafor import Flag, Mute, Orb
from .muteme import MuteMe
from .mutesync import MuteSync
from .plantronics import Status_Indicator
from .thingm import Blink1


__all__ = [
    "Light",
    "HIDLight",
    "SerialLight",
    "LightNotFound",
    "LightUnavailable",
    "LightUnsupported",
    "NoLightsFound",
    "Blink1",
    "BlinkStick",
    "Blynclight",
    "Busylight",
    "Fit_StatUSB",
    "Flag",
    "Mute",
    "MuteMe",
    "MuteSync",
    "Orb",
    "Status_Indicator",
]

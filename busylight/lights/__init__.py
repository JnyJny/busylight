""" Support for USB Connected Lights

"""

from .light import Light
from .hidlight import HIDLight
from .seriallight import SerialLight

from .exceptions import (
    InvalidLightInfo,
    LightUnavailable,
    LightUnsupported,
    NoLightsFound,
)

from .agile_innovative import BlinkStick
from .compulab import Fit_StatUSB
from .embrava import Blynclight, Blynclight_Mini, Blynclight_Plus
from .kuando import Busylight_Alpha, Busylight_Omega
from .luxafor import Flag, Mute, Orb
from .muteme import MuteMe, MuteMe_Mini
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
    "Blynclight_Mini",
    "Blynclight_Plus",
    "Busylight_Alpha",
    "Busylight_Omega",
    "Fit_StatUSB",
    "Flag",
    "Mute",
    "MuteMe",
    "MuteMe_Mini",
    "MuteSync",
    "Orb",
    "Status_Indicator",
]

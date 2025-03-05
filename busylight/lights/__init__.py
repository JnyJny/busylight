"""Support for USB Connected Lights

This package provides abstract and physical classes which implement
support for interacting with USB connected devices.

The Light, HIDLight and SerialLight classes are "abstract". They are
not tied to a particular vendor's device. HIDLight and SerialLight
provide different I/O communication strategies for physical light
subclasses.

Physical lights are organized by vendor packages which in turn contain
the implementations for specific hardware devices. Physical
implementations are subclasses of HIDLight or SerialLight depending on
their specific requirements.

The class methods of the abstract classes, Light, HIDLight and
SerialLight can all be used to discover and interact with increasingly
narrowed devices.  For instance, Light.all_lights() will return a list
of all Light subclasses found, while HIDLight.all_lights() or
SerialLight.all_lights() will only return a list populated with their
respective subclasses.

If you want to filter available lights by vendor, use this
construction:

>>> from busylight.lights import Light
>>> vendor_b = [l for l in Light.all_lights() if l.vendor == "vendor_b"]


The class methods continue to work for physical light subclasses, eg:

>>> from busylight.lights.embrava import Blynclight
>>> Blynclight.all_lights()  # a list populated with only Blynclights


Developers, adding support for a new device will entail:

- Optionally create a new vendor package directory.
- Create a new subclass of HIDDevice or SerialDevice.
- Implement all the missing abstract methods.
- Make sure the vendor package imports all the new subclasses.
- Make sure the vendor package appends the new subclasses to __all__.
- Import the new subclasses in busylight.lights.__init__.
- Add the new subclasses to busylight.lights.__init__.__all__.

Refer to any of the existing vendor packages as an example.

Please note, if the subclasses are not imported here, the
abc.ABC.__subclasses__ machinery will not find them and your
new lights will not be recognized.
"""

from loguru import logger

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
from .busytag import BusyTag
from .compulab import Fit_StatUSB
from .embrava import Blynclight, Blynclight_Mini, Blynclight_Plus
from .kuando import Busylight_Alpha, Busylight_Omega
from .luxafor import Bluetooth, Flag, Mute, Orb
from .muteme import MuteMe, MuteMe_Mini
from .mutesync import MuteSync
from .plantronics import Status_Indicator
from .thingm import Blink1
from .epos import EPOSBusylight


__all__ = [
    "Light",
    "HIDLight",
    "SerialLight",
    "LightUnavailable",
    "LightUnsupported",
    "NoLightsFound",
    "Blink1",
    "BlinkStick",
    "Bluetooth",
    "Blynclight",
    "Blynclight_Mini",
    "Blynclight_Plus",
    "Busylight_Alpha",
    "Busylight_Omega",
    "BusyTag",
    "Fit_StatUSB",
    "Flag",
    "Mute",
    "MuteMe",
    "MuteMe_Mini",
    "MuteSync",
    "Orb",
    "Status_Indicator",
    "EPOSBusylight"
]

logger.disable("busylight.lights")

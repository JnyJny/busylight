"""Support for USB Connected Lights

Developers, adding support for a new device will entail:

- Optionally create a new vendor package in the vendors directory.
- Create a new subclass of busylight_core.light.Light.
- Implement all the missing abstract methods.
- Make sure the vendor package imports all the new subclasses.
- Make sure the vendor package appends the new subclasses to __all__.
- Import the new subclasses in busylight_core.__init__.
- Add the new subclasses to busylight_core.__init__.__all__.

Refer to any of the existing vendor packages as an example.

Note: If the subclasses are not imported here, the
      abc.ABC.__subclasses__ machinery will not find them and your new
      lights will not be recognized.

"""

from importlib.metadata import version

from loguru import logger

from .exceptions import (
    HardwareUnsupportedError,
    InvalidHardwareError,
    LightUnavailableError,
    NoLightsFoundError,
)
from .hardware import Hardware
from .light import Light
from .vendors.agile_innovative import (
    AgileInnovativeLights,
    BlinkStick,
    BlinkStickFlex,
    BlinkStickNano,
    BlinkStickPro,
    BlinkStickSquare,
    BlinkStickStrip,
)
from .vendors.compulab import CompuLabLights, FitStatUSB
from .vendors.embrava import (
    Blynclight,
    BlynclightMini,
    BlynclightPlus,
    Blyncusb10,
    Blyncusb20,
    BlyncusbLights,
    EmbravaLights,
)
from .vendors.epos import Busylight, EPOSLights
from .vendors.kuando import BusylightAlpha, BusylightOmega, KuandoLights
from .vendors.luxafor import Bluetooth, BusyTag, Flag, LuxaforLights, Mute, Orb
from .vendors.muteme import MuteMe, MuteMeLights, MuteMeMini, MuteSync
from .vendors.plantronics import PlantronicsLights, StatusIndicator
from .vendors.thingm import Blink1, ThingMLights

version = version("busylight-core")

__all__ = [
    "AgileInnovativeLights",
    "Blink1",
    "BlinkStick",
    "BlinkStickFlex",
    "BlinkStickNano",
    "BlinkStickPro",
    "BlinkStickSquare",
    "BlinkStickStrip",
    "Bluetooth",
    "Blynclight",
    "BlynclightMini",
    "BlynclightPlus",
    "Blyncusb10",
    "Blyncusb20",
    "BlyncusbLights",
    "BusyTag",
    "Busylight",
    "BusylightAlpha",
    "BusylightOmega",
    "CompuLabLights",
    "EPOSLights",
    "EmbravaLights",
    "FitStatUSB",
    "Flag",
    "Hardware",
    "HardwareUnsupportedError",
    "InvalidHardwareError",
    "KuandoLights",
    "Light",
    "LightUnavailableError",
    "LuxaforLights",
    "Mute",
    "MuteMe",
    "MuteMeLights",
    "MuteMeMini",
    "MuteSync",
    "NoLightsFoundError",
    "Orb",
    "PlantronicsLights",
    "StatusIndicator",
    "ThingMLights",
    "version",
]

logger.disable("busylight_core")

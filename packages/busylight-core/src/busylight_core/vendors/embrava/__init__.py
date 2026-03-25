"""Embrava Device Support"""

from .blynclight import Blynclight
from .blynclight_mini import BlynclightMini
from .blynclight_plus import BlynclightPlus
from .blyncusb10 import Blyncusb10
from .blyncusb20 import Blyncusb20
from .embrava_base import EmbravaBase as EmbravaLights

BlyncusbLights = Blyncusb10  # backwards compat alias

__all__ = [
    "Blynclight",
    "BlynclightMini",
    "BlynclightPlus",
    "Blyncusb10",
    "Blyncusb20",
    "BlyncusbLights",
    "EmbravaLights",
]

"""USB Connected Presence Lights
"""

from .usblight import USBLight
from .exceptions import USBLightNotFound
from .exceptions import USBLightUnknownVendor
from .exceptions import USBLightUnknownProduct
from .exceptions import USBLightInUse
from .exceptions import USBLightIOError

# EJO Some kind of cool dynamic import would be sweet right here.
#     Until then, import each of the light subclasses to make sure they
#     register with the USBLight abstract base class

from .agile_innovative import BlinkStick
from .embrava import Blynclight
from .kuando import Busylight
from .luxafor import Flag
from .plantronics import Status_Indicator
from .thingm import Blink1

__all__ = [
    "USBLight",
    "USBLightNotFound",
    "USBLightUnknownVendor",
    "USBLightUnknownProduct",
    "USBLightInUse",
    "USBLightIOError",
]

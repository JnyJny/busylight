"""USB Connected Presence Lights
"""

from loguru import logger

from .usblight import USBLight
from .exceptions import USBLightNotFound
from .exceptions import USBLightUnknownVendor
from .exceptions import USBLightUnknownProduct
from .exceptions import USBLightInUse
from .exceptions import USBLightIOError

# EJO some kind of cool dynamic import would be sweet right here


from .agile_innovative import BlinkStick
from .embrava import Blynclight
from .plantronics import Status_Indicator

from .kuando import BusyLight
from .luxafor import Flag
from .thingm import Blink1

logger.disable(__name__)

__all__ = [
    "USBLight",
    "USBLightNotFound",
    "USBLightUnknownVendor",
    "USBLightUnknownProduct",
    "USBLightInUse",
    "USBLightIOError",
]

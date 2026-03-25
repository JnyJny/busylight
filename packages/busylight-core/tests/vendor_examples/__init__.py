"""Hardware examples for all supported busylight vendors.

This module provides mock hardware definitions for testing purposes across
all supported busylight vendors and their devices.
"""

from .agile_innovative import AGILE_INNOVATIVE_HARDWARE
from .compulab import COMPULAB_HARDWARE
from .embrava import EMBRAVA_HARDWARE
from .kuando import KUANDO_HARDWARE
from .luxafor import LUXAFOR_HARDWARE
from .muteme import MUTEME_HARDWARE
from .plantronics import PLANTRONICS_HARDWARE
from .thingm import THINGM_HARDWARE

HardwareCatalog = (
    AGILE_INNOVATIVE_HARDWARE
    | COMPULAB_HARDWARE
    | EMBRAVA_HARDWARE
    | KUANDO_HARDWARE
    | LUXAFOR_HARDWARE
    | MUTEME_HARDWARE
    | PLANTRONICS_HARDWARE
    | THINGM_HARDWARE
)

__all__ = [
    "AGILE_INNOVATIVE_HARDWARE",
    "COMPULAB_HARDWARE",
    "EMBRAVA_HARDWARE",
    "KUANDO_HARDWARE",
    "LUXAFOR_HARDWARE",
    "MUTEME_HARDWARE",
    "PLANTRONICS_HARDWARE",
    "THINGM_HARDWARE",
    "HardwareCatalog",
]

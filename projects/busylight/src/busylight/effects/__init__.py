"""Color Effect Generators"""

from loguru import logger

from .blink import Blink
from .effect import BaseEffect as Effects
from .gradient import Gradient
from .spectrum import Spectrum
from .steady import Steady

__all__ = [
    "Blink",
    "Effects",
    "Gradient",
    "Spectrum",
    "Steady",
]

logger.disable("busylight.effects")

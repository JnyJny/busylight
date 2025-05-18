"""Color Effect Generators
"""

from loguru import logger

from .effect import BaseEffect as Effects

from .blink import Blink
from .gradient import Gradient
from .spectrum import Spectrum
from .steady import Steady

__all__ = [
    "Effects",
    "Blink",
    "Gradient",
    "Spectrum",
    "Steady",
]

logger.disable("busylight.effects")

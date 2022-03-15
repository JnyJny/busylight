"""Color Generators
"""


from .effect import BaseEffect as Effects

from .blink import Blink
from .gradient import Gradient
from .spectrum import Spectrum
from .steady import Steady

from .frame import FrameTuple, FrameGenerator


__all__ = [
    "Effects",
    "Blink",
    "Gradient",
    "Spectrum",
    "Steady",
]

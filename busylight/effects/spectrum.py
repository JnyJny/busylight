"""Spectrum Effect

"""
from typing import Generator, Tuple
import math


def Spectrum(
    steps: int = 64,
    frequency: Tuple[float, float, float] = None,
    phase: Tuple[int, int, int] = None,
    center: int = 128,
    width: int = 127,
) -> Generator[Tuple[int, int, int], None, None]:
    """Generator function that returns 'steps' (red, blue, green) tuples.

        steps: optional integer, default=64
    frequency: optional 3-tuple for rbg frequency, default=(.3,.3,.3)
        phase: optional 3-tuple for rbg phase, default=(0,2,4)
       center: optional integer, default=128
        width: optional integer, default=127

    Returns (r, b, g) where each member is a value between 0 and 255.
    """

    rf, bf, gf = frequency or (0.3, 0.3, 0.3)
    phase = phase or (0, 2, 4)

    for i in range(steps):
        r = int((math.sin(rf * i + phase[0]) * width) + center)
        b = int((math.sin(bf * i + phase[2]) * width) + center)
        g = int((math.sin(gf * i + phase[1]) * width) + center)
        yield (r, b, g)

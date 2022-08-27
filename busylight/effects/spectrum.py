""" rainbows are fun!

"""
import math

from itertools import cycle
from typing import List, Tuple

from ..color import scale_color
from .effect import BaseEffect


class Spectrum(BaseEffect):
    """This effect produces colors in the order of the rainbow (ROYGBIV)."""

    def __init__(
        self,
        duty_cycle: float,
        scale: float = 1.0,
        steps: int = 64,
        frequency: Tuple[float, float, float] = None,
        phase: Tuple[int, int, int] = None,
        center: int = 128,
        width: int = 127,
    ) -> None:
        """
        The `scale` parameter scales the intensity of the generated colors.

        :param duty_cycle: float
        :param scale: optional float
        :param steps: optional int
        :param frequency: optional tuple[float, float, float]
        :param phase: optional tuple[int, int, int]
        :param center: optional int
        :param width: optional int
        """

        self.duty_cycle = duty_cycle
        self.scale = max(0, min(scale, 1.0))
        self.steps = steps
        self.frequency = frequency or (0.3, 0.3, 0.3)
        self.phase = phase or (0, 2, 4)
        self.center = center
        self.width = width

    @property
    def colors(self) -> List[Tuple[int, int, int]]:
        try:
            return self._colors
        except AttributeError:
            pass

        rf, bf, gf = self.frequency
        rp, bp, gp = self.phase

        colors = []
        for i in range(self.steps):
            r = int((math.sin(rf * i + rp) * self.width) + self.center)
            b = int((math.sin(bf * i + bp) * self.width) + self.center)
            g = int((math.sin(gf * i + gp) * self.width) + self.center)
            colors.append(scale_color((r, g, b), self.scale))

        self._colors: List[Tuple[int, int, int]] = colors + list(reversed(colors[:-1]))

        return self._colors

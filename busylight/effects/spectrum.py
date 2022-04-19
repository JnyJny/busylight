"""Spectrum Effect

"""
import math

from itertools import cycle
from typing import Tuple

from ..color import ColorList, ColorTuple
from .effect import BaseEffect


class Spectrum(BaseEffect):
    def __init__(
        self,
        duty_cycle: float,
        steps: int = 64,
        frequency: Tuple[float, float, float] = None,
        phase: ColorTuple = None,
        center: int = 128,
        width: int = 127,
    ) -> None:

        self.duty_cycle = duty_cycle

        self.steps = steps
        self.frequency = frequency or (0.3, 0.3, 0.3)
        self.phase = phase or (0, 2, 4)
        self.center = center
        self.width = width

    @property
    def colors(self) -> ColorList:
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
            colors.append((r, g, b))

        self._colors = colors + list(reversed(colors[:-1]))

        return self._colors

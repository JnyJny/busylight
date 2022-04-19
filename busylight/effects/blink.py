"""
"""

from itertools import cycle
from typing import List

from ..color import ColorTuple, ColorList
from .effect import BaseEffect


class Blink(BaseEffect):
    def __init__(
        self,
        on_color: ColorTuple,
        duty_cycle: float,
        off_color: ColorTuple = None,
    ) -> None:
        self.on_color = on_color
        self.off_color = off_color or (0, 0, 0)
        self.duty_cycle = duty_cycle

    def __repr__(self) -> str:
        return f"{self.name}(on_color={self.on_color!r}, duty_cycle={self.duty_cycle!r}, off_color={self.off_color!r})"

    @property
    def duty_cycle(self) -> float:
        return getattr(self, "_duty_cycle", 0)

    @duty_cycle.setter
    def duty_cycle(self, seconds: float) -> None:
        self._duty_cycle = seconds

    @property
    def colors(self) -> ColorList:
        try:
            return self._colors
        except AttributeError:
            pass
        self._colors = cycle([self.on_color, self.off_color])
        return self._colors

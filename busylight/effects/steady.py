"""
"""

from typing import List

from ..color import ColorList, ColorTuple
from .effect import BaseEffect


class Steady(BaseEffect):
    def __init__(self, color: ColorTuple) -> None:
        self.color = color

    def __repr__(self) -> str:
        return f"{self.name}(color={self.color!r})"

    @property
    def duty_cycle(self) -> float:
        return 86400

    @property
    def colors(self) -> ColorList:
        try:
            return self._colors
        except AttributeError:
            pass
        self._colors = [self.color]
        return self._colors

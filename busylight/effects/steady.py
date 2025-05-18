"""
"""

from typing import List, Tuple

from .effect import BaseEffect


class Steady(BaseEffect):
    def __init__(self, color: Tuple[int, int, int]) -> None:
        self.color = color

    def __repr__(self) -> str:
        return f"{self.name}(color={self.color!r})"

    @property
    def duty_cycle(self) -> float:
        return 86400

    @duty_cycle.setter
    def duty_cycle(self, new_value) -> None:
        pass

    @property
    def colors(self) -> List[Tuple[int, int, int]]:
        try:
            return self._colors
        except AttributeError:
            pass
        self._colors: List[Tuple[int, int, int]] = [self.color]
        return self._colors

"""change a light between two colors with a short interval.
"""

from itertools import cycle
from typing import List, Tuple

from .effect import BaseEffect


class Blink(BaseEffect):
    def __init__(
        self,
        on_color: Tuple[int, int, int],
        duty_cycle: float,
        off_color: Tuple[int, int, int] = None,
    ) -> None:
        """This effect turns a light on and off with the specified color(s),
        pausing for `duty_cycle` seconds in between each operation.

        :param on_color: Tuple[int,int,int]
        :param duty_cycle: float
        :param off_color: Tuple[int,int,int] defaults to black.
        """

        self.on_color = on_color
        self.off_color = off_color or (0, 0, 0)
        self.duty_cycle = duty_cycle

    def __repr__(self) -> str:
        return f"{self.name}(on_color={self.on_color!r}, duty_cycle={self.duty_cycle!r}, off_color={self.off_color!r})"

    @property
    def colors(self) -> List[Tuple[int, int, int]]:
        try:
            return self._colors
        except AttributeError:
            pass
        self._colors: List[Tuple[int, int, int]] = [self.on_color, self.off_color]
        return self._colors

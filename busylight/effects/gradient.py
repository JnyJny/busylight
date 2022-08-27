"""a smooth color gradient for a given color.
"""


from itertools import cycle
from typing import List, Tuple

from .effect import BaseEffect


class Gradient(BaseEffect):
    """This effect will produce a color range from black to the
    given color and then back to black again with the given number
    of steps between off and on.
    """

    def __init__(
        self,
        color: Tuple[int, int, int],
        duty_cycle: float,
        step: int = 1,
    ) -> None:
        """
        :param color: Tuple[int,int,int]
        :param duty_cycle: float
        :param step: int
        """

        self.color = color
        self.duty_cycle = duty_cycle
        # XXX need to choose steps that make sense for scaled colors
        #     where the max(color) << 255
        self.step = max(0, min(step, 255))

    @property
    def colors(self) -> List[Tuple[int, int, int]]:
        try:
            return self._colors
        except AttributeError:
            pass

        red, green, blue = self.color

        colors = []
        for i in range(1, 256, self.step):
            scale = i / 255
            r = round(scale * red)
            g = round(scale * green)
            b = round(scale * blue)
            colors.append((r, g, b))

        self._colors: List[Tuple[int, int, int]] = colors + list(reversed(colors[:-1]))

        return self._colors

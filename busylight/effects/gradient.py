"""Color Gradient Effect
"""

from itertools import cycle

from ..color import ColorList, ColorTuple

from .effect import BaseEffect


class Gradient(BaseEffect):
    def __init__(
        self,
        color: ColorTuple,
        duty_cycle: float,
        step: int = 1,
    ) -> None:
        self.color = color
        self.duty_cycle = duty_cycle
        self.step = max(0, min(step, 255))

    @property
    def colors(self) -> ColorList:
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

        self._colors = colors + list(reversed(colors[:-1]))

        return self._colors

"""Color Gradient Effect
"""


from ..color import ColorList, ColorTuple

from .effect import BaseEffect


class Gradient(BaseEffect):
    def __init__(
        self,
        color: ColorTuple,
        step: int = 1,
    ) -> None:
        self.color = color
        self.step = step

    @property
    def colors(self) -> ColorList:
        try:
            return self._colors
        except AttributeError:
            pass

        red, green, blue = self.color

        self._colors = []
        for i in range(1, 256, self.step):
            scale = i / 255
            r = round(scale * red)
            g = round(scale * green)
            b = round(scale * blue)
            self._colors.append((r, g, b))

        self._colors.append(self.color)
        return self._colors

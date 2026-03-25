"""A smooth color gradient for a given color."""

from typing import TYPE_CHECKING

from busylight_core.mixins.taskable import TaskPriority

from .effect import BaseEffect

if TYPE_CHECKING:
    from busylight_core import Light


class Gradient(BaseEffect):
    """This effect produces a smooth color gradient from black to the given
    color and then back to black again with the given number of steps.
    If count is given and is greater than zero the light will cycle through
    the sequence count times.
    """

    def __init__(
        self,
        color: tuple[int, int, int],
        step: int = 1,
        step_max: int = 255,
        count: int = 0,
    ) -> None:
        """Initialize gradient effect.

        :param color: Target RGB color for the gradient
        :param step: Step size for gradient calculation
        :param step_max: Maximum step value, determines gradient smoothness
        :param count: Number of gradient cycles, 0 means infinite
        """
        self.color = color
        self.step = max(1, min(step, step_max))
        self.step_max = step_max
        self.count = count
        self.priority = TaskPriority.LOW

    @property
    def colors(self) -> list[tuple[int, int, int]]:
        if hasattr(self, "_colors"):
            return self._colors

        red, green, blue = self.color
        colors = []

        for i in range(self.step, self.step_max + 1, self.step):
            scale = i / self.step_max
            r = round(scale * red)
            g = round(scale * green)
            b = round(scale * blue)
            colors.append((r, g, b))

        ramp_down = list(reversed(colors[:-1]))
        self._colors: list[tuple[int, int, int]] = colors + ramp_down
        return self._colors

    @property
    def default_interval(self) -> float:
        return 0.1

"""Rainbows are fun!"""

import math
from typing import TYPE_CHECKING

from busylight_core.mixins.taskable import TaskPriority
from loguru import logger

from .effect import BaseEffect

if TYPE_CHECKING:
    from busylight_core import Light


class Spectrum(BaseEffect):
    """This effect produces colors in the order of the rainbow (ROYGBIV)."""

    def __init__(
        self,
        scale: float = 1.0,
        steps: int = 64,
        frequency: tuple[float, float, float] | None = None,
        phase: tuple[int, int, int] | None = None,
        center: int = 128,
        width: int = 127,
        count: int = 0,
    ) -> None:
        """Initialize spectrum effect.

        The `scale` parameter scales the intensity of the generated colors
        and is clamped to the range [0.0, 1.0].

        :param scale: Color intensity scale (0.0 to 1.0)
        :param steps: Number of colors in the spectrum
        :param frequency: RGB frequency tuple for sine wave generation
        :param phase: RGB phase offset tuple for sine wave generation
        :param center: Center value for sine wave
        :param width: Amplitude of sine wave
        :param count: Number of spectrum cycles, 0 means infinite
        """
        logger.debug("initializing")

        self.scale = max(0.0, min(scale, 1.0))
        self.steps = steps
        self.frequency = frequency or (0.3, 0.3, 0.3)
        self.phase = phase or (0, 2, 4)
        self.center = center
        self.width = width
        self.count = count
        self.priority = TaskPriority.LOW

    @property
    def colors(self) -> list[tuple[int, int, int]]:
        if hasattr(self, "_colors"):
            return self._colors

        r_f, g_f, b_f = self.frequency
        r_p, g_p, b_p = self.phase
        colors = []

        for i in range(self.steps):
            rv = r_f * i + r_p
            gv = g_f * i + g_p
            bv = b_f * i + b_p

            r = int((math.sin(rv) * self.width + self.center) * self.scale)
            g = int((math.sin(gv) * self.width + self.center) * self.scale)
            b = int((math.sin(bv) * self.width + self.center) * self.scale)

            colors.append((r, g, b))

        ramp_down = list(reversed(colors[:-1]))
        self._colors: list[tuple[int, int, int]] = colors + ramp_down
        return self._colors

    @property
    def default_interval(self) -> float:
        return 0.05

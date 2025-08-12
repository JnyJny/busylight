"""Steady color effect."""

from typing import TYPE_CHECKING

from busylight_core.mixins.taskable import TaskPriority

from .effect import BaseEffect

if TYPE_CHECKING:
    from busylight_core import Light


class Steady(BaseEffect):
    def __init__(self, color: tuple[int, int, int]) -> None:
        self.color = color
        self.priority = TaskPriority.NORMAL

    def __repr__(self) -> str:
        return f"{self.name}(color={self.color!r})"

    @property
    def colors(self) -> list[tuple[int, int, int]]:
        return [self.color]

    @property
    def default_interval(self) -> float:
        return 0.0

    async def execute(self, light: "Light", interval: float | None = None, led: int = 0) -> None:
        """Execute steady color effect - just set the color once."""
        light.on(self.color, led=led)
        # Steady effect doesn't loop, just sets color and exits

"""Change a light between two colors with a short interval."""

from typing import TYPE_CHECKING

from busylight_core.mixins.taskable import TaskPriority

from .effect import BaseEffect

if TYPE_CHECKING:
    from busylight_core import Light


class Blink(BaseEffect):
    def __init__(
        self,
        on_color: tuple[int, int, int],
        off_color: tuple[int, int, int] | None = None,
        count: int = 0,
    ) -> None:
        """This effect alternates between on_color and off_color.

        If count is given and greater than zero, the light will blink
        count times.

        :param on_color: RGB tuple for the "on" state
        :param off_color: RGB tuple for the "off" state, defaults to black
        :param count: Number of blink cycles, 0 means infinite
        """
        self.on_color = on_color
        self.off_color = off_color or (0, 0, 0)
        self.count = count
        self.priority = TaskPriority.NORMAL

    def __repr__(self) -> str:
        return f"{self.name}(on_color={self.on_color!r}, off_color={self.off_color!r})"

    @property
    def colors(self) -> list[tuple[int, int, int]]:
        return [self.on_color, self.off_color]

    @property
    def default_interval(self) -> float:
        return 0.5

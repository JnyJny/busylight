"""Base class for all effects."""

import abc
import asyncio
from functools import cache
from itertools import cycle, islice
from typing import TYPE_CHECKING

from busylight_core.mixins.taskable import TaskPriority
from loguru import logger

if TYPE_CHECKING:
    from busylight_core import Light


class BaseEffect(abc.ABC):
    @classmethod
    @cache
    def subclasses(cls) -> dict[str, "BaseEffect"]:
        """Returns a dictionary of Effect subclasses, keyed by name."""
        subclasses = {}
        if cls is BaseEffect:
            for subclass in cls.__subclasses__():
                subclasses.update(subclass.subclasses())
            logger.info(f"{cls.__name__} found {len(subclasses)}")
            return subclasses

        subclasses.setdefault(cls.__name__.casefold(), cls)

        for subclass in cls.__subclasses__():
            subclasses.update(subclass.subclasses())

        logger.info(f"{cls.__name__} found {len(subclasses)}")

        return subclasses

    @classmethod
    def for_name(cls, name: str) -> "BaseEffect":
        """Return an effect subclass with the given name.

        :param name: str
        :return: BaseEffect or subclass

        Raises:
        - ValueError for unknown effect names.

        """
        try:
            return cls.subclasses()[name.casefold()]
        except KeyError:
            raise ValueError(f"Unknown effect {name}") from None

    @classmethod
    def effects(cls) -> list[str]:
        """Return a list of effect names."""
        return list(cls.subclasses().keys())

    def __repr__(self) -> str:
        return f"{self.name}(...)"

    def __str__(self) -> str:
        return f"{self.name} count={self.count}"

    @property
    def name(self) -> str:
        """The name of this effect."""
        return self.__class__.__name__

    @property
    def count(self) -> int:
        """Number of cycles to run the effect.

        A count less than or equal to zero means run indefinitely.
        """
        return getattr(self, "_count", 0)

    @count.setter
    def count(self, count: int) -> None:
        self._count = int(count)

    @property
    def priority(self) -> TaskPriority:
        """Task priority for this effect."""
        return getattr(self, "_priority", TaskPriority.NORMAL)

    @priority.setter
    def priority(self, priority: TaskPriority) -> None:
        self._priority = priority

    @property
    @abc.abstractmethod
    def colors(self) -> list[tuple[int, int, int]]:
        """A list of color tuples."""

    @property
    @abc.abstractmethod
    def default_interval(self) -> float:
        """Default interval between color changes in seconds."""

    async def execute(self, light: "Light", interval: float | None = None, led: int = 0) -> None:
        """Execute this effect on the given light.

        This method runs the full effect cycle similar to the original
        generator-based approach but as a single long-running async function.

        :param light: Light instance with TaskableMixin capabilities
        :param interval: Override default interval between color changes
        :param led: LED index to target (0 = all LEDs, 1+ = specific LED)
        """
        sleep_interval = interval if interval is not None else self.default_interval

        if self.count > 0:
            cycle_count = self.count * len(self.colors)
            color_iterator = islice(cycle(self.colors), cycle_count)
        else:
            color_iterator = cycle(self.colors)

        try:
            for color in color_iterator:
                light.on(color, led=led)
                await asyncio.sleep(sleep_interval)
        finally:
            light.off(led=led)

    def reset(self) -> None:
        """Reset the effect's internal state."""
        if hasattr(self, "_color_cycle"):
            delattr(self, "_color_cycle")

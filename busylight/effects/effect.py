"""
"""


import abc
import asyncio

from itertools import cycle
from typing import List, Tuple

from loguru import logger

from ..lights import Light


class BaseEffect(abc.ABC):
    @classmethod
    def subclasses(cls) -> List["BaseEffect"]:
        """Returns a list of Effect subclasses."""
        subclasses = []
        if cls is BaseEffect:
            for subclass in cls.__subclasses__():
                subclasses.extend(subclass.subclasses())
            logger.info(f"{cls.__name__} found {len(subclasses)}")
            return subclasses

        subclasses.append(cls)
        for subclass in cls.__subclasses__():
            subclasses.extend(subclass.subclasses())
        logger.info(f"{cls.__name__} found {len(subclasses)}")
        return subclasses

    @classmethod
    def for_name(cls, name: str) -> "BaseEffect":
        """Finds an effect subclass with the given name.

        :param name: str
        :return: BaseEffect or subclass

        Raises:
        - ValueError for unknown effect names.
        """
        casefolded_name = name.casefold()
        for subclass in cls.subclasses():
            if subclass.__name__.casefold() == casefolded_name:
                return subclass
        else:
            raise ValueError(f"Unknown effect {name}")

    def __repr__(self) -> str:

        return f"{self.name}(...)"

    def __str__(self) -> str:

        return f"{self.name} duty_cycle={self.duty_cycle}"

    @property
    def name(self) -> str:
        """The name of this effect."""
        return self.__class__.__name__

    @property
    def duty_cycle(self) -> float:
        """Interval in seconds for current frame of the effect to be displayed."""
        return getattr(self, "_duty_cycle", 0)

    @duty_cycle.setter
    def duty_cycle(self, seconds: float) -> None:
        self._duty_cycle = seconds

    @property
    @abc.abstractmethod
    def colors(self) -> List[Tuple[int, int, int]]:
        """A list of color tuples."""

    async def __call__(self, light: Light) -> None:
        """Apply this effect to the given light.

        :param light: Light
        """
        for color in cycle(self.colors):
            light.on(color)
            await asyncio.sleep(self.duty_cycle)

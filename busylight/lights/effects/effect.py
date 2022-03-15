"""
"""


import abc

from itertools import cycle
from typing import List

from loguru import logger

from ..color import ColorList, ColorTuple
from .frame import FrameGenerator, FrameTuple


class BaseEffect(abc.ABC):
    @classmethod
    def subclasses(cls) -> List["BaseEffect"]:
        """Returns a list of Effect subclasses."""
        subclasses = []
        if cls is BaseEffect:
            for subclass in cls.__subclasses__():
                subclasses.extend(subclass.subclasses())
            logger.debug(f"{cls.__name__} found {len(subclasses)}")
            return subclasses

        subclasses.append(cls)
        for subclass in cls.__subclasses__():
            subclasses.extend(subclass.subclasses())
        logger.debug(f"{cls.__name__} found {len(subclasses)}")
        return subclasses

    @classmethod
    def for_name(cls, name: str) -> "BaseEffect":

        casefolded_name = name.casefold()
        for subclass in cls.subclasses():
            if subclass.__name__.casefold() == casefolded_name:
                return subclass
        else:
            raise ValueError(f"Unknown effect {name}")

    def __repr__(self) -> str:

        return f"{self.name}(...)"

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    @abc.abstractmethod
    def duty_cycle(self) -> float:
        """Interval in seconds for current frame of the effect to be displayed."""

    @property
    @abc.abstractmethod
    def colors(self) -> ColorList:
        """A list of color tuples."""

    def __call__(
        self,
        repeat: bool = True,
        reverse: bool = False,
        duty_cycle: float = None,
    ) -> FrameGenerator:

        if duty_cycle is None:
            duty_cycle = self.duty_cycle

        colors = self.colors
        if reverse:
            colors += reverse(self.colors)
        colors = cycle(colors) if repeat else colors

        for color in colors:
            yield (color, duty_cycle)

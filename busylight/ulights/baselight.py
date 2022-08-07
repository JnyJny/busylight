""" The Most Basic of Lights
"""

import abc

from typing import Union


class BaseLight(abc.ABC, tuple[int, int, int]):
    @property
    @abc.abstractmethod
    def color(self) -> tuple[int, int, int]:
        """A three channel color value."""

    @color.setter
    @abc.abstractmethod
    def color(self, new_value: tuple[int, int, int]) -> None:
        """"""

    @abc.abstractmethod
    def on(self, color: tuple[int, int, int]) -> None:
        """Turn the light on with the supplied color tuple."""

    @abc.abstractmethod
    def off(self) -> None:
        """Turn the light off."""

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset the light to a known state."""

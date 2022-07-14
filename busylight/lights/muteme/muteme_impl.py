""" MuteMe implementation details
"""

from enum import Enum

from loguru import logger

from ...color import ColorTuple, colortuple_to_name, ColorLookupError


class MuteMeUnknownColor(Exception):
    def __str__(self) -> str:
        return f"Color {self.args[0]} not in {list(MuteMeColor.__members__.keys())}"


class MuteMeEffect(int, Enum):
    dim = 0x10
    blink_fast = 0x20
    blink_slow = 0x30


class MuteMeTouch(int, Enum):
    clear = 0x00
    touching = 0x01
    end = 0x02
    start = 0x04


class MuteMeColor(int, Enum):
    black = 0x00
    red = 0x01
    green = 0x02
    yellow = 0x03
    blue = 0x04
    purple = 0x05
    cyan = 0x06
    white = 0x07

    @classmethod
    def from_colortuple(
        cls,
        color: ColorTuple,
        dim: bool = False,
        blink: int = 0,
    ) -> int:
        try:
            name = colortuple_to_name(color)
            logger.info(f"{color=} {name=}")
            return getattr(cls, name.lower())

        except ColorLookupError:
            logger.info(f"no name for {color}")
        except AttributeError:
            logger.info(f"name {name} not defined for MuteMe")

        r, g, b = color
        if r and not g and not b:
            return cls.red

        if g and not r and not b:
            return cls.green

        if b and not r and not g:
            return cls.blue

        raise MuteMeUnknownColor(color)

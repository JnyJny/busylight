"""
"""

from enum import IntEnum
from typing import Tuple

from bitvector import BitField, BitVector


class Action(IntEnum):
    SetColor = 0x1202

class Report(IntEnum):
    One = 1

class ReportField(BitField):
    """An 8-bit report field."""


class ActionField(BitField):
    """An 8-bit action."""


class ColorField(BitField):
    """An 8-bit color value."""

class OnField(BitField):
    """A 1-bit field that toggles the light on."""

class Command(BitVector):
    """"""

    def __init__(self):
        super().__init__(0, 80)
        self.default = 0

    report = ReportField(72, 8)
    action = ActionField(56, 16)

    red1 = ColorField(48, 8)
    green1 = ColorField(40, 8)
    blue1 = ColorField(32, 8)

    red2 = ColorField(24, 8)
    green2 = ColorField(16, 8)
    blue2 = ColorField(8, 8)

    on = OnField(0, 8)
    

    def set_color(
        self,
        color: Tuple[int, int, int],
    ) -> None:
        """ """
        self.reset()
        self.report = Report.One
        self.action = Action.SetColor
        self.color = color
        self.on = 0 if color == (0,0,0) else 1
        
    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, color: Tuple[int, int, int]) -> None:
        self.red1, self.green1, self.blue1 = color  # type: ignore
        self.red2, self.green2, self.blue2 = color  # type: ignore

    def reset(self) -> None:
        """Reset command state to default value."""
        self.value = self.default

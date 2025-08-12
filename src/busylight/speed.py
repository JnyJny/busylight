"""Describe how often to change colors."""

from enum import Enum, auto
from functools import cached_property


class Speed(str, Enum):
    Slow = "slow"
    Medium = "medium"
    Fast = "fast"

    @cached_property
    def duty_cycle(self) -> float:
        """Duty cycle in seconds."""
        return {
            "Slow": 0.75,
            "Medium": 0.5,
            "Fast": 0.25,
        }.get(self.name, 0.75)

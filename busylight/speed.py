""" Describe how often to change colors.
"""

from enum import Enum


class Speed(str, Enum):
    Slow = "slow"
    Medium = "medium"
    Fast = "fast"

    @property
    def duty_cycle(self) -> float:
        """Duty cycle in seconds."""
        try:
            return self._duty_cycle
        except AttributeError:
            pass
        self._duty_cycle: float = {0: 0.75, 1: 0.5, 2: 0.25}.get(self.rate, 0)
        return self._duty_cycle

    @property
    def rate(self) -> int:
        return ["slow", "medium", "fast"].index(self.name.lower())

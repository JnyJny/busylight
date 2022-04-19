"""
"""

from enum import Enum


class Speed(str, Enum):
    Slow = "slow"
    Medium = "medium"
    Fast = "fast"

    @property
    def duty_cycle(self) -> float:
        try:
            return self._duty_cycle
        except AttributeError:
            pass
        self._duty_cycle = {0: 0.75, 1: 0.5, 2: 0.25}.get(self.rate, 0)
        return self._duty_cycle

    @property
    def rate(self) -> int:
        return ["slow", "medium", "fast"].index(self.name.lower())


#    def __bool__(self) -> bool:
#        return self != Speed.Stop

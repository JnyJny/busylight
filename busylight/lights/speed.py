"""
"""

from enum import Enum


class Speed(str, Enum):
    Stop = "stop"
    Slow = "slow"
    Medium = "medium"
    Fast = "fast"

    @property
    def duty_cycle(self) -> float:
        try:
            return self._duty_cycle
        except AttributeError:
            pass
        self._duty_cycle = {1: 0, 1: 0.75, 2: 0.5, 3: 0.25}.get(self.rate, 0)
        return self._duty_cycle

    @property
    def rate(self) -> int:
        try:
            return self._rate
        except AttributeError:
            pass
        self._rate = ["stop", "slow", "medium", "fast"].index(self.name.lower())
        return self._rate

    def __bool__(self) -> bool:
        return self != Speed.Stop

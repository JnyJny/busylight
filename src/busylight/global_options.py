""""""

from dataclasses import dataclass, field

from .manager import LightManager


@dataclass
class GlobalOptions:
    timeout: float = None
    dim: float = 0
    lights: list[int] = field(default_factory=list)
    debug: bool = False
    manager: LightManager = field(default_factory=LightManager)

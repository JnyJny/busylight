""""""

from dataclasses import dataclass, field

from .controller import LightController


@dataclass
class GlobalOptions:
    timeout: float = None
    dim: float = 0
    lights: list[int] = field(default_factory=list)
    debug: bool = False
    controller: LightController = field(default_factory=LightController)

"""Support for the Luxafor Flag USB light
"""

from enum import Enum
from typing import cast, List, Tuple


from .hardware import FlagState
from .hardware import FlagLED
from .hardware import FlagWave
from .hardware import FlagPattern
from .hardware import FlagColorCommand
from .hardware import FlagStrobeCommand

from ..usblight import USBLight


class Flag(USBLight):
    """Support for the Luxafor Flag USB light."""

    VENDOR_IDS: List[int] = [0x04D8]
    PRODUCT_IDS: List[int] = []
    vendor = "Luxafor"

    @property
    def state(self) -> FlagState:
        """Implementation dependent hardware state."""
        try:
            return self._state
        except AttributeError:
            pass
        self._state: FlagState = FlagState()
        return self._state

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            pass

        self._name: str = str(self.info.get("product_string", "Luxafor Flag (maybe)"))
        return self._name

    def __bytes__(self):
        return bytes(self.state)

    def reset(self):
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        super().on(color)

        command = FlagColorCommand(color)
        with self.batch_update():
            self.state.reset()
            self.state.value = command.value

    def blink(self, color: Tuple[int, int, int], speed: int = 1):

        super().blink(color, speed)

        command = FlagStrobeCommand(color, 0xF - speed, 0)
        with self.batch_update():
            self.state.reset()
            self.state.value = command.value

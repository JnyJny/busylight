"""Support for the Luxafor Flag USB light
"""

from enum import Enum
from typing import Tuple


from .hardware import FlagState
from .hardware import FlagLED
from .hardware import FlagWave
from .hardware import FlagPattern
from .hardware import FlagCommand

from ..usblight import USBLight


class Flag(USBLight):
    """Support for the Luxafor Flag USB light."""

    VENDOR_IDS = [0x04D8]
    PRODUCT_IDS = []
    vendor = "Luxafor"

    @property
    def state(self) -> FlagState:
        try:
            return self._state
        except AttributeError:
            pass
        self._state = FlagState()
        return self._state

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            pass
        self._name = self.info["product_string"].title()
        return self._name

    @property
    def is_on(self) -> bool:
        return any(self.color)

    def reset(self):
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        self.color = color

        with self.batch_update():
            self.state.reset()
            self.state.cmd = FlagCommand.COLOR
            self.state.leds = FlagLED.ALL
            self.state.color = color

    def off(self):

        self.on((0, 0, 0))

    def blink(self, color: Tuple[int, int, int], speed: int = 0):

        self.color = color

        with self.batch_update():
            self.state.reset()
            self.state.cmd = FlagCommand.STROBE
            self.state.leds = FlagLED.ALL
            self.state.color = color
            self.state.strobe_speed = 0xF - speed
            self.state.strobe_repeat = 0

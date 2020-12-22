"""Support for ThingM Blink Lights
"""

from typing import Tuple

from .usblight import USBLight
from .statevector import StateVector, StateField


class Blink1State(StateVector):
    def __init__(self):
        super().__init__(0, 0)


class Blink1(USBLight):

    VENDOR_IDS = [0x27B8]
    PRODUCT_IDS = []
    __vendor__ = "ThingM"
    __family__ = "Blink"

    @property
    def state(self):
        try:
            return self._state
        except AttributeError:
            pass
        self._state = Blink1State()
        return self._state

    @property
    def color(self) -> Tuple[int, int, int]:
        pass

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        pass

    @property
    def is_on(self) -> bool:
        pass

    def reset(self) -> None:
        pass

    def on(self, color: Tuple[int, int, int]) -> None:
        pass

    def off(self):
        pass

    def blink(self, color: Tuple[int, int, int], speed: int = 0) -> None:
        pass

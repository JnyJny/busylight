"""Support for Kuando Busylights
"""

from typing import Tuple

from .usblight import USBLight
from .statevector import StateVector, StateField


class BusyLightState(StateVector):
    def __init__(self):
        super().__init__(0, 0)


class BusyLight(USBLight):

    VENDOR_IDS = [0x27BB]
    PRODUCT_IDS = []
    __vendor__ = "Kuando"
    __family__ = "BusyLight"

    @property
    def state(self):
        try:
            return self._state
        except AttributeError:
            pass
        self._state = BusyLightState()
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

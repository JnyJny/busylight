"""Support for Kuando Busylights
"""

from typing import Tuple

from .hardware import BusyLightState

from ..usblight import USBLight


class BusyLight(USBLight):

    VENDOR_IDS = [0x27BB]
    PRODUCT_IDS = []
    vendor = "Kuando"

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

"""Support for Embrava Blynclights
"""


from typing import Tuple

from .hardware import BlynclightState

from ..usblight import USBLight


class Blynclight(USBLight):
    """Embrava Blynclight family of USB-connected presence lights."""

    VENDOR_IDS = [0x2C0D, 0x03E5]
    PRODUCT_IDS = []
    vendor = "Embrava"

    @property
    def state(self):
        try:
            return self._state
        except AttributeError:
            pass
        self._state = BlynclightState()
        return self._state

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.state.red, self.state.green, self.state.blue)

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self.state.red, self.state.green, self.state.blue = values

    @property
    def is_on(self) -> bool:
        return not self.state.off

    def __bytes__(self):
        return bytes(self.state)

    def reset(self) -> None:
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        with self.batch_update():
            self.color = color
            self.state.flash = False
            self.state.speed = 1
            self.state.off = False

    def off(self) -> None:

        with self.batch_update():
            self.state.off = True
            self.state.flash = False
            self.state.speed = 1

    def blink(self, color: Tuple[int, int, int] = None, speed: int = 0) -> None:

        with self.batch_update():
            if color:
                self.color = color
            self.state.off = False
            self.state.flash = True
            self.state.speed = 1 << speed

"""Support for Embrava Blynclights
"""


from typing import List, Tuple

from .hardware import BlynclightState

from ..usblight import USBLight


class Blynclight(USBLight):
    """Embrava Blynclight family of USB-connected presence lights."""

    VENDOR_IDS: List[int] = [0x2C0D, 0x03E5]
    PRODUCT_IDS: List[int] = []
    vendor = "Embrava"

    @property
    def state(self) -> BlynclightState:
        """Implementation dependent hardware state."""
        try:
            return self._state
        except AttributeError:
            pass
        self._state: BlynclightState = BlynclightState()
        return self._state

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.state.red, self.state.green, self.state.blue)

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self.state.red, self.state.green, self.state.blue = values  # type: ignore

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
            self.state.flash = 0  # type: ignore
            self.state.speed = 1  # type: ignore
            self.state.off = 0  # type: ignore

    def off(self) -> None:

        with self.batch_update():
            self.state.off = 1  # type: ignore
            self.state.flash = 0  # type: ignore
            self.state.speed = 1  # type: ignore

    def blink(self, color: Tuple[int, int, int], speed: int = 1) -> None:

        super().blink(color, speed)

        with self.batch_update():
            if color:
                self.color = color
            self.state.off = 0  # type: ignore
            self.state.flash = 1  # type: ignore
            self.state.speed = 1 << (speed - 1)  # type: ignore

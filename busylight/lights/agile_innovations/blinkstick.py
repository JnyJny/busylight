"""Support for Agile Innovations BlinkSticks
"""

from functools import partial
from time import sleep
from typing import Tuple

from .hardware import BlinkStickState, BlinkStickVariant

from ..usblight import USBLight
from ...effects import blink as blink_effect


class BlinkStick(USBLight):

    VENDOR_IDS = [0x20A0]
    PRODUCT_IDS = []
    vendor = "Agile Innovations"

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            pass
        self._name = str(BlinkStickVariant.identify(self))
        return self._name

    @property
    def state(self):
        """Implementation dependent hardware state."""
        try:
            return self._state
        except AttributeError:
            pass
        self._state = BlinkStickState()
        return self._state

    def __bytes__(self):
        return bytes(self.state)

    def reset(self) -> None:
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        super().on(color)

        color = color[1], color[0], color[2]

        with self.batch_update():
            self.state.report = 6
            self.state.channel = 0
            self.state.led0 = color
            self.state.led1 = color
            self.state.led2 = color
            self.state.led3 = color
            self.state.led4 = color
            self.state.led5 = color
            self.state.led6 = color
            self.state.led7 = color

    def blink(self, color: Tuple[int, int, int], speed: int = 1) -> None:

        super().blink(color, speed)

        self.start_animation(partial(blink_effect, color=color, speed=speed))

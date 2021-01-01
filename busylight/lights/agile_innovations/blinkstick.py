"""Support for Agile Innovations BlinkSticks
"""

from functools import partial
from time import sleep
from typing import Tuple

from .hardware import BlinkStickState, BlinkStickVariant

from ..usblight import USBLight

from ..statevector import StateVector, StateField


def _blink_animation(
    light: USBLight,
    color: Tuple[int, int, int],
    speed: int = 1,
) -> None:

    interval = {1: 1.0, 2: 0.5, 3: 0.25}.get(speed, 1.0)

    while True:
        light.on(color)
        yield
        sleep(interval)
        light.off()
        yield
        sleep(interval)


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
        try:
            return self._state
        except AttributeError:
            pass
        self._state = BlinkStickState()
        return self._state

    def reset(self) -> None:
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        self.color = color

        r, g, b = color
        color = g, r, b

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

    def off(self):

        self.on((0, 0, 0))

    def blink(self, color: Tuple[int, int, int], speed: int = 0) -> None:

        self.start_animation(partial(_blink_animation, color=color, speed=speed))

"""Support for Agile Innovative BlinkSticks
"""

from functools import partial
from typing import List, Tuple

from .hardware import BlinkStickVariant

from ..usblight import USBLight
from ...effects import blink as blink_effect


class BlinkStick(USBLight):

    VENDOR_IDS: List[int] = [0x20A0]
    PRODUCT_IDS: List[int] = []
    vendor = "Agile Innovative"

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            pass
        self._name: str = self.variant.name
        return self._name

    @property
    def variant(self) -> BlinkStickVariant:
        try:
            return self._variant
        except AttributeError:
            pass
        self._variant: BlinkStickVariant = BlinkStickVariant.identify(self.info)
        return self._variant

    @property
    def state(self):
        """Implementation dependent hardware state."""
        return self.variant.state

    def __bytes__(self):
        return bytes(self.state)

    def reset(self) -> None:
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        super().on(color)

        color = color[1], color[0], color[2]

        with self.batch_update():
            self.state.reset()
            self.state.color(color)

    def blink(self, color: Tuple[int, int, int], speed: int = 1) -> None:

        super().blink(color, speed)

        self.start_animation(partial(blink_effect, color=color, speed=speed))

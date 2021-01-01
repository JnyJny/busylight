"""Support for ThingM Blink Lights
"""

from enum import Enum
from typing import Tuple

from .hardware import Blink1Report, Blink1Action, Blink1LED, Blink1State

from ..usblight import USBLight


class Blink1(USBLight):

    VENDOR_IDS = [0x27B8]
    PRODUCT_IDS = []
    vendor = "ThingM"

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
        return getattr(self, "_color", (0, 0, 0))

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self._color = tuple(values)

    @property
    def is_on(self) -> bool:
        return any(self.color)

    def reset(self) -> None:
        self.state.reset()

    def update(self) -> None:
        """Updates the hardware with the current software state.

        Raises:
        - USBLightIOError
          The light may have been unplugged.
          The light may have been released.
        """
        try:
            nbytes = self.device.send_feature_report(self.state.bytes)
        except ValueError as error:
            raise USBLightIOError(str(error)) from None
        if nbytes != len(self.state.bytes):
            raise USBLightIOError(f"send_feature_report returned {nbytes}") from None

    def on(self, color: Tuple[int, int, int]) -> None:
        self.fade(color)

    def off(self):
        self.fade((0, 0, 0))

    def blink(self, color: Tuple[int, int, int], speed: int = 0) -> None:

        activate = 10
        decay = 100 // (speed + 1)

        self.color = color

        self.write_pattern_line(color, activate, 0)
        self.write_pattern_line((0, 0, 0), decay, 1)
        self.save_patterns()
        self.play_loop(1, 0, 1)

    def fade(
        self,
        color: Tuple[int, int, int],
        time_ms: int = 10,
        leds: Blink1LED = Blink1LED.ALL,
    ) -> None:
        self.color = color
        with self.batch_update():
            self.state.reset()
            self.state.report = Blink1Report.ONE
            self.state.action = Blink1Action.FadeColor
            self.state.color = color
            self.state.fade = time_ms
            self.state.leds = leds

    def write_pattern_line(
        self, color: Tuple[int, int, int], fade_ms: int, index: int
    ) -> None:

        with self.batch_update():
            self.state.reset()
            self.state.report = Blink1Report.ONE
            self.state.action = Blink1Action.SetColorPattern
            self.state.color = color
            self.state.fade = fade_ms
            self.state.line = index

    def save_patterns(self):

        with self.batch_update():
            self.state.reset()
            self.state.report = Blink1Report.ONE
            self.state.action = Blink1Action.SaveColorPatterns
            self.state.color = (0xBE, 0xEF, 0xCA)
            self.state.count = 0xFE

    def play_loop(self, play: int, start: int, stop: int, count: int = 0) -> None:

        with self.batch_update():
            self.state.reset()
            self.state.report = Blink1Report.ONE
            self.state.action = Blink1Action.PlayLoop
            self.state.play = play
            self.state.start = start
            self.state.stop = stop
            self.state.count = count

    def clear_patterns(self, start: int = 0, count: int = 16) -> None:

        for index in range(start, start + count):
            self.write_pattern_line((0, 0, 0), 0, index)

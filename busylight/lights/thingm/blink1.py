"""Support for ThingM Blink Lights
"""

from enum import Enum
from typing import Callable, Tuple

from .hardware import Blink1Report, Blink1Action, Blink1LED, Blink1State

from ..usblight import USBLight


class Blink1(USBLight):

    VENDOR_IDS = [0x27B8]
    PRODUCT_IDS = []
    vendor = "ThingM"

    @property
    def state(self):
        """Implementation dependent hardware state."""
        try:
            return self._state
        except AttributeError:
            pass
        self._state = Blink1State()
        return self._state

    @property
    def strategy(self) -> Callable:
        """Returns the write function used for IO to the device."""
        return self.device.send_feature_report

    def __bytes__(self):
        return bytes(self.state)

    def reset(self) -> None:
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        super().on(color)
        self.fade(color, time_ms=0)

    def blink(self, color: Tuple[int, int, int], speed: int = 1) -> None:

        super().blink(color, speed)

        activate = 10
        decay = 100 // (speed + 1)

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
        """
        :param color: Tuple[int, int, int]
        :param time_ms: int = 10
        :param leds: Blink1LED = Blink1LED.ALL
        """
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
        """
        :param color: Tuple[int, int, int]
        :param fade_ms: int
        :param index: int
        """

        with self.batch_update():
            self.state.reset()
            self.state.report = Blink1Report.ONE
            self.state.action = Blink1Action.SetColorPattern
            self.state.color = color
            self.state.fade = fade_ms
            self.state.line = index

    def save_patterns(self):
        """"""
        with self.batch_update():
            self.state.reset()
            self.state.report = Blink1Report.ONE
            self.state.action = Blink1Action.SaveColorPatterns
            self.state.color = (0xBE, 0xEF, 0xCA)
            self.state.count = 0xFE

    def play_loop(self, play: int, start: int, stop: int, count: int = 0) -> None:
        """
        :param play: int
        :param start: int
        :param stop: int
        :param count: int = 0
        """
        with self.batch_update():
            self.state.reset()
            self.state.report = Blink1Report.ONE
            self.state.action = Blink1Action.PlayLoop
            self.state.play = play
            self.state.start = start
            self.state.stop = stop
            self.state.count = count

    def clear_patterns(self, start: int = 0, count: int = 16) -> None:
        """
        :param start: int = 0
        :param count: int = 16
        """
        for index in range(start, start + count):
            self.write_pattern_line((0, 0, 0), 0, index)

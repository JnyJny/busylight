"""ThingM Blink support.
"""

from enum import Enum
from typing import Tuple

from .usblight import USBLight
from .usblight import USBLightAttribute, USBLightImmediateAttribute
from .usblight import UnknownUSBLight


class Blink1Action(int, Enum):
    FadeColor = ord("c")
    SetColor = ord("n")
    ReadColor = ord("r")
    ServerTickle = ord("D")
    PlayLoop = ord("p")
    PlayStateRead = ord("S")
    SetColorPattern = ord("P")
    SaveColorPatterns = ord("W")
    ReadColorPattern = ord("R")
    SetLEDn = ord("l")
    ReadEEPROM = ord("e")
    WriteEEPROM = ord("E")
    GetVersion = ord("v")
    TestCommand = ord("!")
    WriteNote = ord("F")
    ReadNote = ord("f")
    Bootloader = ord("G")
    LockBootLoader = ord("L")
    SetStartupParams = ord("B")
    GetStartupParams = ord("b")
    ServerModeTickle = ord("D")
    GetChipID = ord("U")


class Blink1LED(int, Enum):
    ALL = 0
    TOP = 1
    BOTTOM = 2


class Blink1Report(int, Enum):
    ONE = 1
    TWO = 2


class Blink1(USBLight):
    VENDOR_IDS = [0x27B8]
    __vendor__ = "ThingM"

    def __init__(self, vendor_id: int, product_id: int):

        if vendor_id not in self.VENDOR_IDS:
            raise UnknownUSBLight(vendor_id)

        super().__init__(vendor_id, product_id, 0, 64)

        self.report == Blink1Report.ONE
        self.default_fade = 10
        self.immediate_mode = True

    report = USBLightAttribute(56, 8)
    action = USBLightAttribute(48, 8)

    red = USBLightAttribute(40, 8)
    play = USBLightAttribute(40, 8)

    green = USBLightAttribute(32, 8)
    start = USBLightAttribute(32, 8)

    blue = USBLightAttribute(24, 8)
    stop = USBLightAttribute(24, 8)

    count = USBLightAttribute(16, 8)
    fade = USBLightAttribute(8, 16)

    leds = USBLightAttribute(0, 8)
    line = USBLightAttribute(0, 8)

    def read(self, buf):
        rc = self.device.send_feature_report(buf)

        return self.device.get_feature_report(buf[0], 8)

    def update(self, flush: bool = False) -> None:
        """Writes the in-memory state of the device to the hardware.

        The update is skipped if immediate_mode is False and flush
        is False. If flush is True, the value of immediate_mode is
        ignored.

        Note: ThingM Blink(1) communicates via the USB feature
        report mechanism and *not* vanilla write operations. Writing
        to the device will cause it to lockup and stop responding.

        :param flush: bool
        """

        if flush or self.immediate_mode:
            self.device.send_feature_report(self.bytes)

    def on(self, color: Tuple[int, int, int] = None) -> None:
        """Turn the light on with the specified color [default=green].
        """
        self.b1_fade_to_color(color, self.default_fade)

    def off(self) -> None:
        """Turn the light off.
        """
        self.b1_fade_to_color((0, 0, 0), self.default_fade)

    def blink(self, color: Tuple[int, int, int] = None, speed: int = 1) -> None:
        """Turn the light on with specified color [default=red] and begin blinking.

        :param color: Tuple[int, int, int]
        :param speed: 1 == slow, 2 == medium, 3 == fast
        """

        if not any(color):
            color = (255, 0, 0)

        activate = 10
        decay = 100 // speed

        self.b1_write_pattern_line(color, activate, 0)
        self.b1_write_pattern_line((0, 0, 0), decay, 1)
        self.b1_save_patterns()
        self.b1_play_loop(1, 0, 1)

    def b1_fade_to_color(
        self, color: Tuple[int, int, int], time_ms: int, leds: Blink1LED = Blink1LED.ALL
    ) -> None:
        """
        """
        with self.updates_paused():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.FadeColor
            self.color = color
            self.fade = time_ms
            self.leds = leds

    def b1_set_color_now(self, color: Tuple[int, int, int]) -> None:
        """Only of devices with fw val 204+
        """
        with self.updates_paused():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.SetColor
            self.color = color

    def b1_write_pattern_line(
        self, color: Tuple[int, int, int], fade_ms: int, pos: int
    ) -> None:
        """
        """
        with self.updates_paused():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.SetColorPattern
            self.color = color
            self.fade = fade_ms
            self.line = pos

    def b1_save_patterns(self):
        """
        """
        with self.updates_paused():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.SaveColorPatterns
            self.red = 0xBE
            self.green = 0xEF
            self.blue = 0xCA
            self.count = 0xFE

    def b1_play_loop(self, play: int, start: int, stop: int, count: int = 0) -> None:
        """
        """
        with self.updates_paused():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.PlayLoop
            self.play = play
            self.start = start
            self.stop = stop
            self.count = count

    def b1_clear_patterns(self, start: int = 0, count: int = 16):
        """
        """
        for n in range(start, start + count):
            self.b1_write_pattern_line((0, 0, 0), 0, n)

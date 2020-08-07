"""ThingM blink(1) support.
"""

from enum import Enum
from typing import Tuple

from .usblight import USBLight
from .usblight import USBLightAttribute
from .usblight import UnknownUSBLight
from .usblight import USBLightIOError


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


class Blink1ReportField(USBLightAttribute):
    """An 8-bit report field."""


class Blink1ActionField(USBLightAttribute):
    """An 8-bit action."""


class Blink1ColorField(USBLightAttribute):
    """An 8-bit color value."""


class Blink1PlayField(USBLightAttribute):
    """An 8-bit value.
    """


class Blink1StartField(USBLightAttribute):
    """An 8-bit value."""


class Blink1StopField(USBLightAttribute):
    """An 8-bit value."""


class Blink1CountField(USBLightAttribute):
    """An 8-bit count value."""


class Blink1FadeField(USBLightAttribute):
    """An 8-bit fade duty cycle value."""


class Blink1LEDSField(USBLightAttribute):
    """An 8-bit field."""


class Blink1LineField(USBLightAttribute):
    """An 8-bit field."""


class Blink1(USBLight):
    """ThingM blink(1) USB connnected LED light.
    
    """

    VENDOR_IDS = [0x27B8]
    __vendor__ = "ThingM"

    def __init__(self, vendor_id: int, product_id: int):
        """
        :param vendor_id: 16-bit integer
        :param product_id: 16-bit integer

        Raises:
        - UnknownUSBLight
        - USBLightInUse
        - USBLightNotFound
        """

        super().__init__(vendor_id, product_id, (Blink1Report.ONE << 56), 64)
        self.default_fade = 10

    report = Blink1ReportField(56, 8)
    action = Blink1ActionField(48, 8)

    red = Blink1ColorField(40, 8)
    play = Blink1PlayField(40, 8)

    green = Blink1ColorField(32, 8)
    start = Blink1StartField(32, 8)

    blue = Blink1ColorField(24, 8)
    stop = Blink1StopField(24, 8)

    count = Blink1CountField(16, 8)
    fade = Blink1FadeField(8, 16)

    leds = Blink1LEDSField(0, 8)
    line = Blink1LineField(0, 8)

    def write(self) -> int:
        """Write the in-memory state of the device to hardware.

        The ThingM blink(1) uses the `send_feature_report` interface
        instead of the `write` interface. 
        
        :return: int number of bytes written.
        
        """
        result = self.device.send_feature_report(self.bytes)

        if result != len(self.bytes):
            raise USBLightIOError(self, result)

        return result

    def impl_on(self, color: Tuple[int, int, int]) -> None:
        """Turn the light on with the specified color.
        """
        self.fade_to_color(color, self.default_fade)

    def impl_off(self) -> None:
        """Turn the light off.
        """
        self.fade_to_color((0, 0, 0), self.default_fade)

    def impl_blink(self, color: Tuple[int, int, int], speed: int) -> None:
        """Turn the light on with specified color [default=red] and begin blinking.

        :param color: Tuple[int, int, int]
        :param speed: 1 == slow, 2 == medium, 3 == fast
        """

        if not any(color):
            color = (255, 0, 0)

        activate = 10
        decay = 100 // speed

        self.write_pattern_line(color, activate, 0)
        self.write_pattern_line((0, 0, 0), decay, 1)
        self.save_patterns()
        self.play_loop(1, 0, 1)

    def fade_to_color(
        self, color: Tuple[int, int, int], time_ms: int, leds: Blink1LED = Blink1LED.ALL
    ) -> None:
        """
        :param color: Tuple[int, int, int]
        :param time_ms: int
        :param leds: Blink1Led
        """
        with self.batch_update():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.FadeColor
            self.color = color
            self.fade = time_ms
            self.leds = leds

    def set_color_now(self, color: Tuple[int, int, int]) -> None:
        """Only of devices with fw val 204+

        :param color: Tuple[int, int, int]
        """

        with self.batch_update():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.SetColor
            self.color = color

    def write_pattern_line(
        self, color: Tuple[int, int, int], fade_ms: int, pos: int
    ) -> None:
        """
        :param color: Tuple[int, int, int]
        :param fade_ms: int
        :param pos: int
        """
        with self.batch_update():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.SetColorPattern
            self.color = color
            self.fade = fade_ms
            self.line = pos

    def save_patterns(self):
        """
        """
        with self.batch_update():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.SaveColorPatterns
            self.red = 0xBE
            self.green = 0xEF
            self.blue = 0xCA
            self.count = 0xFE

    def play_loop(self, play: int, start: int, stop: int, count: int = 0) -> None:
        """
        :param play: int
        :param start: int
        :param stop: int
        :param count: int
        """
        with self.batch_update():
            self.clear()
            self.report = Blink1Report.ONE
            self.action = Blink1Action.PlayLoop
            self.play = play
            self.start = start
            self.stop = stop
            self.count = count

    def clear_patterns(self, start: int = 0, count: int = 16):
        """
        :param start: int
        :param count: int
        """
        for n in range(start, start + count):
            self.write_pattern_line((0, 0, 0), 0, n)

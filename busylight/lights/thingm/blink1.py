"""Support for ThingM Blink Lights
"""

from enum import Enum
from typing import Tuple

from .usblight import USBLight
from .statevector import StateVector, StateField


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


class Blink1ReportField(StateField):
    """An 8-bit report field."""


class Blink1ActionField(StateField):
    """An 8-bit action."""


class Blink1ColorField(StateField):
    """An 8-bit color value."""


class Blink1PlayField(StateField):
    """An 8-bit value."""


class Blink1StartField(StateField):
    """An 8-bit value."""


class Blink1StopField(StateField):
    """An 8-bit value."""


class Blink1CountField(StateField):
    """An 8-bit count value."""


class Blink1FadeField(StateField):
    """An 8-bit fade duty cycle value."""


class Blink1LEDSField(StateField):
    """An 8-bit field."""


class Blink1LineField(StateField):
    """An 8-bit field."""


class Blink1State(StateVector):
    """"""

    def __init__(self):
        super().__init__(Blink1Report.ONE << 56, 64)

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

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self.red, self.green, self.blue = values


class Blink1(USBLight):

    VENDOR_IDS = [0x27B8]
    PRODUCT_IDS = []
    __vendor__ = "ThingM"

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

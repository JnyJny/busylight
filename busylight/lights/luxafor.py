"""Support for the Luxafor Flag USB light
"""

from enum import Enum
from typing import Tuple

from .usblight import USBLight
from .statevector import StateVector, StateField


class FlagCmdAttribute(StateField):
    """Luxafor Flag mode command."""


class FlagLEDAttribute(StateField):
    """Luxafor Flag LED selector."""


class FlagPatternAttribute(StateField):
    """Luxafor Flag pattern value."""


class FlagWaveAttribute(StateField):
    """Luxafor Flag wave value."""


class FlagColorAttribute(StateField):
    """An 8-bit color value."""


class FlagRepeatAttribute(StateField):
    """Luxafor Flag repeat value."""


class FlagFadeAttribute(StateField):
    """Luxafor Flag fade speed value."""


class FlagSpeedAttribute(StateField):
    """Luxafor Flag speed value."""


class FlagLED(int, Enum):
    ALL = 0xFF
    BACK = 0x41
    FRONT = 0x42
    LED1 = 0x1
    LED2 = 0x2
    LED3 = 0x3
    LED4 = 0x4
    LED5 = 0x5
    LED6 = 0x6


class FlagWave(int, Enum):
    OFF = 0
    WAVE1 = 1
    WAVE2 = 2
    WAVE3 = 3
    WAVE4 = 4
    WAVE5 = 5


class FlagPattern(int, Enum):
    OFF = 0
    PATTERN1 = 1
    PATTERN2 = 2
    PATTERN3 = 3
    PATTERN4 = 4
    PATTERN5 = 5
    PATTERN6 = 6
    PATTERN7 = 7
    PATTERN8 = 8


class FlagCommand(int, Enum):
    COLOR = 1
    STROBE = 3
    WAVE = 4
    PATTERN = 6


class FlagState(StateVector):
    """Luxafor Flag State Vector"""

    def __init__(self):
        super().__init__(0x1FF000000000000, 64)

    # The Luxafor Flag command buffer isn't regular so there are some fields
    # that are aliased to make code more straightforward.

    cmd = FlagCmdAttribute(56, 8)

    # aliases: led, pattern, wave
    leds = FlagLEDAttribute(48, 8)
    pattern = FlagPatternAttribute(48, 8)
    wave = FlagWaveAttribute(48, 8)

    # aliases: red, pattern_repeat
    red = FlagColorAttribute(40, 8)
    pattern_repeat = FlagRepeatAttribute(40, 8)

    green = FlagColorAttribute(32, 8)
    blue = FlagColorAttribute(24, 8)

    # aliases: fade, strobe_speed
    fade = FlagFadeAttribute(16, 8)
    strobe_speed = FlagSpeedAttribute(16, 8)

    wave_repeat = FlagRepeatAttribute(8, 8)

    # aliases: wave_speed, strobe_repeat
    strobe_repeat = FlagRepeatAttribute(0, 8)
    wave_speed = FlagSpeedAttribute(0, 8)

    @property
    def color(self):
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, values: Tuple[int, int, int]):
        self.red, self.green, self.blue = values


class Flag(USBLight):
    """Support for the Luxafor Flag USB light."""

    VENDOR_IDS = [0x04D8]
    PRODUCT_IDS = []
    __vendor__ = "Luxafor"

    @property
    def state(self) -> FlagState:
        try:
            return self._state
        except AttributeError:
            pass
        self._state = FlagState()
        return self._state

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            pass
        self._name = self.info["product_string"].title()
        return self._name

    @property
    def color(self) -> Tuple[int, int, int]:
        return getattr(self, "_color", (0, 0, 0))

    @color.setter
    def color(self, values: Tuple[int, int, int]):
        self._color = tuple(values)

    @property
    def is_on(self) -> bool:
        return any(self.color)

    def reset(self):
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        self.color = color

        with self.batch_update():
            self.state.reset()
            self.state.cmd = FlagCommand.COLOR
            self.state.leds = FlagLED.ALL
            self.state.color = color

    def off(self):

        self.on((0, 0, 0))

    def blink(self, color: Tuple[int, int, int], speed: int = 0):

        self.color = color

        with self.batch_update():
            self.state.reset()
            self.state.cmd = FlagCommand.STROBE
            self.state.leds = FlagLED.ALL
            self.state.color = color
            self.state.strobe_speed = 0xF - speed
            self.state.strobe_repeat = 0

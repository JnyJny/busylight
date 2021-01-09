"""
"""
from enum import Enum
from typing import Tuple

from ..statevector import StateVector, StateField


class CommandField(StateField):
    """An 8-bit command format selector."""


class LEDField(StateField):
    """An 8-bit LED selector."""


class PatternField(StateField):
    """An 8-bit pattern value."""


class WaveField(StateField):
    """An 8-bit wave value."""


class ColorField(StateField):
    """An 8-bit color value."""


class RepeatField(StateField):
    """An 8-bit repeat value."""


class FadeField(StateField):
    """An 8-bit fade speed value."""


class SpeedField(StateField):
    """An 8-bit speed value."""


class PadField(StateField):
    """Pad bits, unused."""


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
    FADE = 2
    STROBE = 3
    WAVE = 4
    PATTERN = 6


class FlagColorCommand(StateVector):
    def __init__(
        self, color: Tuple[int, int, int], fade: int = 0, leds: FlagLED = FlagLED.ALL
    ):

        value = (FlagCommand.FADE if fade else FlagCommand.COLOR) << 56
        super().__init__(value, 64)
        self.leds = leds  # type: ignore
        self.color = color
        self.fade = fade  # type:ignore

    command = CommandField(56, 8)
    leds = LEDField(48, 8)
    red = ColorField(40, 8)
    green = ColorField(32, 8)
    blue = ColorField(24, 8)
    fade = FadeField(16, 8)
    pad = PadField(0, 16)

    @property
    def color(self):
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, values: Tuple[int, int, int]):
        self.red, self.green, self.blue = values  # type: ignore


class FlagStrobeCommand(StateVector):
    def __init__(
        self,
        color: Tuple[int, int, int],
        speed: int,
        repeat: int,
        leds: FlagLED = FlagLED.ALL,
    ):
        super().__init__(0x300000000000000, 64)
        self.leds = leds  # type: ignore
        self.color = color
        self.speed = speed  # type: ignore
        self.repeat = repeat  # type: ignore

    command = CommandField(56, 8)
    leds = LEDField(48, 8)
    red = ColorField(40, 8)
    green = ColorField(32, 8)
    blue = ColorField(24, 8)
    speed = SpeedField(16, 8)
    pad = PadField(8, 16)
    repeat = RepeatField(0, 8)


class FlagWaveCommand(StateVector):
    def __init__(self):
        super().__init__(0x400000000000000, 64)

    command = CommandField(56, 8)
    wave = WaveField(48, 8)
    red = ColorField(40, 8)
    green = ColorField(32, 8)
    blue = ColorField(24, 8)
    pad = PadField(16, 8)
    repeat = RepeatField(8, 8)
    speed = SpeedField(0, 8)


class FlagPatternCommand(StateVector):
    def __init__(self):
        super().__init__(0x600000000000000, 64)

    command = CommandField(56, 8)
    pattern = PatternField(48, 8)
    repeat = RepeatField(40, 8)
    pad = PadField(0, 40)


class FlagState(StateVector):
    """Luxafor Flag State Vector"""

    def __init__(self):
        super().__init__(0x1FF000000000000, 64)

    # The Luxafor Flag command buffer isn't regular so there are some fields
    # that are aliased to make code more straightforward.

    cmd = CommandField(56, 8)

    # aliases: led, pattern, wave
    leds = LEDField(48, 8)
    pattern = PatternField(48, 8)
    wave = WaveField(48, 8)

    # aliases: red, pattern_repeat
    red = ColorField(40, 8)
    pattern_repeat = RepeatField(40, 8)

    green = ColorField(32, 8)
    blue = ColorField(24, 8)

    # aliases: fade, strobe_speed
    fade = FadeField(16, 8)
    strobe_speed = SpeedField(16, 8)

    wave_repeat = RepeatField(8, 8)

    # aliases: wave_speed, strobe_repeat
    strobe_repeat = RepeatField(0, 8)
    wave_speed = SpeedField(0, 8)

    @property
    def color(self):
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, values: Tuple[int, int, int]):
        self.red, self.green, self.blue = values  # type: ignore

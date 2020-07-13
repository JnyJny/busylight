"""Luxafor Flag support.
"""

from enum import Enum
from typing import Tuple

from .usblight import USBLight, USBLightAttribute
from .usblight import UnknownUSBLight


class FlagAttribute(USBLightAttribute):
    """Base Luxafor Flag attribute.
    """


class FlagCmdAttribute(FlagAttribute):
    """Luxafor Flag mode command."""


class FlagLEDAttribute(FlagAttribute):
    """Luxafor Flag LED selector."""


class FlagPatternAttribute(FlagAttribute):
    """Luxafor Flag pattern value."""


class FlagWaveAttribute(FlagAttribute):
    """Luxafor Flag wave value."""


class FlagColorAttribute(FlagAttribute):
    """An 8-bit color value."""


class FlagRepeatAttribute(FlagAttribute):
    """Luxafor Flag repeat value."""


class FlagFadeAttribute(FlagAttribute):
    """Luxafor Flag fade speed value."""


class FlagSpeedAttribute(FlagAttribute):
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


class Flag(USBLight):

    VENDOR_IDS = [0x04D8]

    __vendor__ = "Luxafor"

    def __init__(self, vendor_id: int, product_id: int):
        """A Luxafor Flag device.

        :param vendor_id: 16-bit integer
        :param product_id: 16-bit integer

        Raises:
        - UnknownUSBLight
        - USBLightInUse
        - USBLightNotFound
        """

        if vendor_id not in self.VENDOR_IDS:
            raise UnknownUSBLight(vendor_id)

        super().__init__(vendor_id, product_id, 0, 64)
        self.immediate_mode = True
        self.off()

    # The Luxafor Flag command buffer isn't regular
    # so there are some fields that are aliased to make
    # the controlling code more straight forward.

    cmd = FlagCmdAttribute(56, 8)

    leds = FlagLEDAttribute(48, 8)
    pattern = FlagPatternAttribute(48, 8)
    wave = FlagWaveAttribute(48, 8)

    red = FlagColorAttribute(40, 8)
    pattern_repeat = FlagRepeatAttribute(40, 8)

    green = FlagColorAttribute(32, 8)
    blue = FlagColorAttribute(24, 8)

    fade = FlagFadeAttribute(16, 8)
    strobe_speed = FlagSpeedAttribute(16, 8)

    wave_repeat = FlagRepeatAttribute(8, 8)

    strobe_repeat = FlagRepeatAttribute(0, 8)
    wave_speed = FlagSpeedAttribute(0, 8)

    def on(self, color: Tuple[int, int, int] = None) -> None:
        """Turn the light on with specified color [default=green]. 

        :param color: Tuple[int, int, int]:
        """
        with self.updates_paused():
            color = color or self.color
            if not any(color):
                color = (0, 255, 0)
            self.lf_activate(FlagLED.ALL, color, 0)

    def off(self) -> None:
        """Turn the light off.
        """
        self.lf_activate(FlagLED.ALL, (0, 0, 0), 0)

    def blink(self, color: Tuple[int, int, int] = None, speed: int = 1) -> None:
        """Turn the light on with specified color [default=red] and begin blinking.

        :param color: Tuple[int, int, int]
        :param speed: 1 == slow, 2 == medium, 3 == fast
        """

        if not color:
            color = (255, 0, 0)

        if speed >= 0:
            speed = 0xF - speed
            self.lf_strobe(FlagLED.ALL, color, speed)
        else:
            self.off()

    def lf_activate(
        self, leds: FlagLED, color: Tuple[int, int, int], fade: int = 0,
    ) -> None:
        """Sets the specifed LEDs to the given color with a fade time.

        :param leds: luxafor.FlagLED
        :param color: Tuple[int, int, int]
        :param fade: int
        """
        with self.updates_paused():
            self.reset()
            self.cmd = FlagCommand.COLOR
            self.leds = leds
            self.color = color
            if fade > 0:
                self.leds = FlagLED.LED2
                self.fade = fade

    def lf_strobe(
        self, leds: FlagLED, color: Tuple[int, int, int], speed: int, repeat: int = 0,
    ) -> None:
        """Begins strobing the specifed leds with given color at speed for repeat iterations.
        
        :param leds: luxfor.FlagLED
        :param color: Tuple[int, int, int]
        :param speed: int
        :param repeat: int [default=0, forever]

        """
        with self.updates_paused():
            self.reset()
            self.cmd = FlagCommand.STROBE
            self.leds = leds
            self.color = color
            self.strobe_speed = speed
            self.strobe_repeat = repeat

    def lf_wave(
        self, wave: FlagWave, color: Tuple[int, int, int], speed: int, repeat: int = 0,
    ) -> None:
        """Begins a wave pattern with the given color at speed for repeat iterations.

        :param wave: luxafor.FlagWave
        :param color: Tuple[int, int, int]
        :param speed: int
        :param repeat: int [default=0, forever]
        """
        with self.updates_paused():
            self.reset()
            self.cmd = FlagCommand.WAVE
            self.color = color
            self.wave_repeat = repeat
            self.wave_speed = speed

    def lf_pattern(self, pattern: FlagPattern, repeat: int = 0) -> None:
        """Begins a flashing a pattern for repeat iterations.

        :param pattern: luxafor.FlagPattern
        :param repeat: int [default=0, forever]
        """
        with self.updates_paused():
            self.reset()
            self.cmd = FlagCommand.PATTERN
            self.pattern = pattern
            self.pattern_repeat = repeat
            self.update()

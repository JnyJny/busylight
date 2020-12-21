"""Support for Embrava Blynclights
"""


from typing import Tuple

from .usblight import USBLight
from .statevector import StateVector, StateField, ReadOnlyStateField


class BlynclightStateHeader(ReadOnlyStateField):
    """A 16-bit constant field whose value is zero."""


class BlynclightColor(StateField):
    """An 8-bit color value."""


class BlynclightOff(StateField):
    """A 1-bit field that toggles the light off."""


class BlynclightDim(StateField):
    """A 1-bit field that toggles dim mode on."""


class BlynclightFlash(StateField):
    """A 1-bit field that toggles flash mode on."""


class BlynclightSpeed(StateField):
    """A 3-bit field that specifies the flash speed.

    b000 : invalid
    b001 : slow
    b010 : medium
    b100 : fast
    """


class BlynclightRepeat(StateField):
    """A 1 bit field that toggles tune repeat mode on."""


class BlynclightPlay(StateField):
    """A 1-bit field that toggles playing the selected tune."""


class BlynclightMusic(StateField):
    """A 4-bit field that selects a firmware tune to play.

    Valid values range from 1 to 10.
    """


class BlynclightMute(StateField):
    """A 1-bit field that toggles muting the tune being played."""


class BlynclightVolume(StateField):
    """A 4-bit field controlling the volume of the tune when played.

    Valid values range from 0 to 10, corresponding to percentage of
    maximum volume. I think.
    """


class BlynclightStateFooter(ReadOnlyStateField):
    """A 16-bit constant field with value 0xFF22."""


class BlynclightState(StateVector):
    """Blynclight State

    A bit-wise representation of the command format
    expected by the Blynclight family of devices.

    The command format is nine bytes in length;
    the first byte is constant zero and the final
    two bytes are constant 0xff22. The intervening
    bits control various functionality of the light.

    The field bit length and names are:
    8 : constant 0
    8 : red
    8 : blue
    8 : green
    1 : off
    1 : dim
    1 : flash
    3 : speed
    1 : repeat
    1 : play
    4 : music
    1 : mute
    4 : volume
    16: constant 0xff22
    """

    def __init__(self):
        super().__init__(0x00000000090080FF22, 72)

    header = BlynclightStateHeader(64, 8)
    red = BlynclightColor(56, 8)
    blue = BlynclightColor(48, 8)
    green = BlynclightColor(40, 8)
    off = BlynclightOff(32, 1)
    dim = BlynclightDim(33, 1)
    flash = BlynclightFlash(34, 1)
    speed = BlynclightSpeed(35, 3)
    repeat = BlynclightRepeat(29, 1)
    play = BlynclightPlay(28, 1)
    music = BlynclightMusic(24, 4)
    mute = BlynclightMute(23, 1)
    volume = BlynclightVolume(18, 4)
    footer = BlynclightStateFooter(0, 16)


class Blynclight(USBLight):
    """Embrava Blynclight family of USB-connected presence lights."""

    VENDOR_IDS = [0x2C0D, 0x03E5]
    PRODUCT_IDS = []
    __vendor__ = "Embrava"
    __family__ = "Blynclight"

    @property
    def state(self):
        try:
            return self._state
        except AttributeError:
            pass
        self._state = BlynclightState()
        return self._state

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.state.red, self.state.green, self.state.blue)

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self.state.red, self.state.green, self.state.blue = values

    @property
    def is_on(self) -> bool:
        return not self.state.off

    def reset(self):
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        with self.batch_update():
            self.color = color
            self.state.flash = False
            self.state.speed = 1
            self.state.off = False

    def off(self) -> None:

        with self.batch_update():
            self.state.off = True
            self.state.flash = False
            self.state.speed = 1

    def blink(self, color: Tuple[int, int, int] = None, speed: int = 0) -> None:

        with self.batch_update():
            if color:
                self.color = color
            self.state.off = False
            self.state.flash = True
            self.state.speed = 1 << speed

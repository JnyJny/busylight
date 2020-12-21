"""Support for Embrava Blynclights
"""

from bitvector import BitField, ReadOnlyBitField
from typing import Tuple

from .usblight import USBLight
from .state import State


class BlynclightStateHeader(ReadOnlyBitField):
    """A constant 16-bit field with zero value."""


class BlynclightColor(BitField):
    """An 8-bit color."""


class BlynclightOff(BitField):
    """Toggle the light off and on: 1 == off, 0 == on."""


class BlynclightDim(BitField):
    """Toggle the light from bright to dim. bright == 0, dim == 1."""


class BlynclightFlash(BitField):
    """Toggle the light from steady to flash mode."""


class BlynclightSpeed(BitField):
    """A four bit field that specifies the flash speed."""


class BlynclightRepeat(BitField):
    """Toggle tune repeat: 0 once, 1 repeat"""


class BlynclightPlay(BitField):
    """Toggle playing selected tune."""


class BlynclightMusic(BitField):
    """Select a tune in firmware: 0 - 10"""


class BlynclightMute(BitField):
    """Toggle muting the tune being played. 0 == play, 1 == mute."""


class BlynclightVolume(BitField):
    """Volume of the tune when played: 0 - 10"""


class BlynclightStateFooter(ReadOnlyBitField):
    """A 16-bit constant field with value 0xFF22."""


class BlynclightState(State):
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

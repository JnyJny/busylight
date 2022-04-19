"""
"""
from bitvector import BitVector, BitField, ReadOnlyBitField

from ...color import ColorTuple


class BlynclightCmdHeader(ReadOnlyBitField):
    """A 16-bit constant field whose value is zero."""


class BlynclightColor(BitField):
    """An 8-bit color value."""


class BlynclightOff(BitField):
    """A 1-bit field that toggles the light off."""


class BlynclightDim(BitField):
    """A 1-bit field that toggles dim mode on."""


class BlynclightFlash(BitField):
    """A 1-bit field that toggles flash mode on."""


class BlynclightSpeed(BitField):
    """A 3-bit field that specifies the flash speed.

    b000 : invalid
    b001 : slow
    b010 : medium
    b100 : fast
    """


class BlynclightRepeat(BitField):
    """A 1 bit field that toggles tune repeat mode on."""


class BlynclightPlay(BitField):
    """A 1-bit field that toggles playing the selected tune."""


class BlynclightMusic(BitField):
    """A 4-bit field that selects a firmware tune to play.

    Valid values range from 1 to 10.
    """


class BlynclightMute(BitField):
    """A 1-bit field that toggles muting the tune being played."""


class BlynclightVolume(BitField):
    """A 4-bit field controlling the volume of the tune when played.

    Valid values range from 0 to 10, corresponding to percentage of
    maximum volume. I think.
    """


class BlynclightCmdFooter(ReadOnlyBitField):
    """A 16-bit constant field with value 0xFF22."""


class BlynclightCommand(BitVector):
    """Blynclight Command

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
    2 : pad

    4 : music
    1 : play
    1 : repeat
    2 : pad

    4 : volume
    1 : mute
    3 : pad

    16: constant 0xff22
    """

    def __init__(self):
        super().__init__(0x00000000090080FF22, 72)
        self.default = self.value

    def reset(self):
        self.value = self.default

    @property
    def color(self) -> ColorTuple:
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, new_color: ColorTuple) -> None:
        self.red, self.green, self.blue = new_color

    header = BlynclightCmdHeader(64, 8)
    red = BlynclightColor(56, 8)
    blue = BlynclightColor(48, 8)
    green = BlynclightColor(40, 8)

    off = BlynclightOff(32, 1)
    dim = BlynclightDim(33, 1)
    flash = BlynclightFlash(34, 1)
    speed = BlynclightSpeed(35, 3)
    # 2 bit pad
    music = BlynclightMusic(28, 4)
    play = BlynclightPlay(27, 1)
    repeat = BlynclightRepeat(26, 1)
    # 2 bit pad
    volume = BlynclightVolume(20, 4)
    mute = BlynclightMute(19, 1)
    # 3 bit pad
    footer = BlynclightCmdFooter(0, 16)

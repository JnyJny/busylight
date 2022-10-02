""" Embrava Blynclight Implementation Details
"""
from bitvector import BitVector, BitField, ReadOnlyBitField


class Header(ReadOnlyBitField):
    """A 16-bit constant field whose value is zero."""


class ColorField(BitField):
    """An 8-bit color value."""


class OffField(BitField):
    """A 1-bit field that toggles the light off."""


class DimField(BitField):
    """A 1-bit field that toggles dim mode on."""


class FlashField(BitField):
    """A 1-bit field that toggles flash mode on."""


class SpeedField(BitField):
    """A 3-bit field that specifies the flash speed.

    b000 : invalid
    b001 : slow
    b010 : medium
    b100 : fast
    """


class RepeatField(BitField):
    """A 1 bit field that toggles tune repeat mode on."""


class PlayField(BitField):
    """A 1-bit field that toggles playing the selected tune."""


class MusicField(BitField):
    """A 4-bit field that selects a firmware tune to play.

    Valid values range from 1 to 10.
    """


class MuteField(BitField):
    """A 1-bit field that toggles muting the tune being played."""


class VolumeField(BitField):
    """A 4-bit field controlling the volume of the tune when played.

    Valid values range from 0 to 10, corresponding to percentage of
    maximum volume. I think.
    """


class Footer(ReadOnlyBitField):
    """A 16-bit constant field with value 0xFF22."""


class Command(BitVector):
    """Blynclight Command

    A bit-wise representation of the command format expected by the
    Blynclight family of devices.

    The command format is nine bytes in length; the first byte is
    constant zero and the final two bytes are constant 0xff22. The
    intervening bits control various functionality of the light.

    typedef struct {
      unsigned int header:8; /* constant 0x00 */
      unsigned int red:8;
      unsigned int blue:8;
      unsigned int green:8;

      unsigned int off:1;
      unsigned int dim:1;
      unsigned int flash:1;
      unsigned int speed:3;
      unsigned int pad0:2;

      unsigned int music:4;
      unsigned int play:1;
      unsigned int repeat:1;
      unsigned int pad1:2;

      unsigned int volume:4;
      unsigned int mute:1;
      unsigned int pad2:3;

      unsigned int footer:16; /* constant 0xff22 */
    }

    """

    def __init__(self):
        super().__init__(0x00000000090080FF22, 72)
        self.default = self.value

    def reset(self):
        self.value = self.default

    header = Header(64, 8)
    red = ColorField(56, 8)
    blue = ColorField(48, 8)
    green = ColorField(40, 8)

    off = OffField(32, 1)
    dim = DimField(33, 1)
    flash = FlashField(34, 1)
    speed = SpeedField(35, 3)
    # 2 bit pad
    music = MusicField(28, 4)
    play = PlayField(27, 1)
    repeat = RepeatField(26, 1)
    # 2 bit pad
    volume = VolumeField(20, 4)
    mute = MuteField(19, 1)
    # 3 bit pad
    footer = Footer(0, 16)

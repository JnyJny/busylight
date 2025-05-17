""" MuteMe Implementation Details
"""

from typing import Tuple

from bitvector import BitVector, BitField, ReadOnlyBitField

from loguru import logger


class Header(ReadOnlyBitField):
    """An 8-bit constant field whose value is zero."""


class ColorField(BitField):
    """A 1-bit color value."""


class ReservedField(ReadOnlyBitField):
    """A 1-bit constant field reserved for future use."""


class DimField(BitField):
    """A 1-bit field that toggles dim mode on."""


class BlinkField(BitField):
    """A 2-bit field that toggles blink mode off/slow/flast."""


class SleepField(BitField):
    """A 1-bit field that toggles the device's auto-sleep mode."""


class Command(BitVector):
    """MuteMe Command

    A bit-wise representation of the command format expected by the
    MuteMe family of devices.

    The command format is two bytes in length; the first byte is constant
    zero and the second byte consists of five bit fields that control the
    functionality of the light.

    typedef struct {
      unsigned int header:8;
      unsigned int pad:1;
      unsigned int sleep:1;
      unsigned int blink:1;
      unsigned int dim:1;
      unsigned int blue:1;
      unsigned int green:1;
      unsigned int red:1;
    }

    Note: This device can only display 8 colors due to the 3-bit color
          versus the typical 24-bit color in other devices.
    """

    def __init__(self):
        super().__init__(0x00, 16)
        self.default = self.value

    header = Header(8, 8)
    # bit 7 unused?

    sleep = SleepField(6, 1)
    _blink = BlinkField(5, 1)
    dim = DimField(4, 1)

    reserved = ReservedField(3, 1)
    blue = ColorField(2, 1)
    green = ColorField(1, 1)
    red = ColorField(0, 1)

    def reset(self):
        self.value = self.default

    @property
    def color(self) -> Tuple[int, int, int]:
        color = (self.red, self.green, self.blue)
        r, g, b = [255 if value else 0 for value in color]
        return (r, g, b)

    @color.setter
    def color(self, new_color: Tuple[int, int, int]) -> None:
        r, g, b = new_color
        self.red = int(bool(r))
        self.green = int(bool(g))
        self.blue = int(bool(b))

    @property
    def firmware_update(self) -> bool:
        """Use not recommended."""
        return bool(self.reserved and self.red)

    @firmware_update.setter
    def firmware_update(self, value: bool) -> None:
        self.reserved = int(bool(value))
        self.red = int(bool(value))

    @property
    def blink(self) -> int:
        if self._blink:
            return self._blink + self.dim
        return 0

    @blink.setter
    def blink(self, value: int) -> None:
        if value == 0:
            self._blink = 0
        if value == 1:
            self._blink = 1
        if value == 2:
            self._blink = 1
            self.dim = 1

"""MuteMe device state management.

This module defines the State class that manages command construction
for MuteMe devices, including simple on/off color control and device
behavior settings.
"""

from busylight_core.word import Word

from .fields import BlinkBit, BlueBit, DimBit, GreenBit, RedBit, SleepBit


class State(Word):
    """Complete device state for MuteMe commands.

    MuteMe devices have a simple control scheme using 1-bit fields for
    each color component and behavior setting. Unlike other vendors,
    MuteMe uses pure on/off color control rather than full 8-bit RGB values.
    """

    red = RedBit()
    green = GreenBit()
    blue = BlueBit()
    dim = DimBit()
    blink = BlinkBit()
    sleep = SleepBit()

    @property
    def color(self) -> tuple[int, int, int]:
        """Get the current color state as RGB tuple.

        Returns 8-bit RGB values (0x00 or 0xFF) based on the
        current bit field states.
        """
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, values: tuple[int, int, int]) -> None:
        """Set the color state from RGB tuple.

        Any non-zero color component will set the corresponding bit,
        zero values will clear the bit.

        :param values: RGB tuple with any numeric values (converted to boolean)
        """
        self.red, self.green, self.blue = values

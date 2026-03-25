"""MuteMe bit field definitions.

This module defines BitField classes used to construct device commands.
MuteMe devices use 1-bit fields that are converted to full 8-bit values
for device communication.
"""

from busylight_core.word import BitField, Word


class OneBitField(BitField):
    """Base class for 1-bit fields that expand to full 8-bit values.

    MuteMe devices expect 0xFF for "on" state and 0x00 for "off" state,
    but internally we work with boolean-like values for simplicity.
    """

    def __get__(self, instance: Word, owner: type | None = None) -> int:
        """Get field value, converting 1-bit to 8-bit representation."""
        return 0xFF if super().__get__(instance, owner) else 0

    def __set__(self, instance: Word, value: int) -> None:
        """Set field value, converting any truthy value to 1-bit."""
        super().__set__(instance, int(bool(value)))


class RedBit(OneBitField):
    """1-bit red color field that expands to 0xFF when set."""

    def __init__(self) -> None:
        super().__init__(0, 1)


class GreenBit(OneBitField):
    """1-bit green color field that expands to 0xFF when set."""

    def __init__(self) -> None:
        super().__init__(1, 1)


class BlueBit(OneBitField):
    """1-bit blue color field that expands to 0xFF when set."""

    def __init__(self) -> None:
        super().__init__(2, 1)


class DimBit(OneBitField):
    """1-bit dim field for brightness control."""

    def __init__(self) -> None:
        super().__init__(4, 1)


class BlinkBit(OneBitField):
    """1-bit blink field for flashing control."""

    def __init__(self) -> None:
        super().__init__(5, 1)


class SleepBit(OneBitField):
    """1-bit sleep field for power management."""

    def __init__(self) -> None:
        super().__init__(6, 1)

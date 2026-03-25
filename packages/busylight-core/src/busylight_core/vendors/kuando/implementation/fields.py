"""Kuando Busylight bit field definitions.

This module defines BitField classes used to construct device commands.
Each field represents a specific portion of the 64-bit command structure
that controls various aspects of the Kuando Busylight device behavior.
"""

from busylight_core.word import BitField, Word


class OpCodeField(BitField):
    """4-bit opcode"""

    def __init__(self) -> None:
        super().__init__(60, 4)


class OperandField(BitField):
    """4-bit operand"""

    def __init__(self) -> None:
        super().__init__(56, 4)


class BodyField(BitField):
    """56-bit body"""

    def __init__(self) -> None:
        super().__init__(0, 56)


class RepeatField(BitField):
    """8-bit repeat"""

    def __init__(self) -> None:
        super().__init__(48, 8)


class ScaledColorField(BitField):
    """A scaled color field that converts between 0-255 RGB values and device scale.

    The Kuando devices use a 0-100 internal scale for color values, but the
    public API uses standard 0-255 RGB values. This field handles the conversion
    automatically when getting and setting color values.
    """

    def __get__(self, instance: Word | None, owner: type | None = None) -> int:
        if instance is None:
            return self
        return (instance[self.field] / 100) * 0xFF

    def __set__(self, instance: Word, value: int) -> None:
        instance[self.field] = int((value / 0xFF) * 100)


class RedField(ScaledColorField):
    """8-bit red color component with automatic scaling."""

    def __init__(self) -> None:
        super().__init__(40, 8)


class GreenField(ScaledColorField):
    """8-bit green color component with automatic scaling."""

    def __init__(self) -> None:
        super().__init__(32, 8)


class BlueField(ScaledColorField):
    """8-bit blue color component with automatic scaling."""

    def __init__(self) -> None:
        super().__init__(24, 8)


class DutyCycleOnField(BitField):
    """8-bit duty cycle on time for LED pulsing patterns."""

    def __init__(self) -> None:
        super().__init__(16, 8)


class DutyCycleOffField(BitField):
    """8-bit duty cycle off time for LED pulsing patterns."""

    def __init__(self) -> None:
        super().__init__(8, 8)


class UpdateBit(BitField):
    """1-bit update"""

    def __init__(self) -> None:
        super().__init__(7, 1)


class RingtoneField(BitField):
    """4-bit ringtone selection field."""

    def __init__(self) -> None:
        super().__init__(3, 4)


class VolumeField(BitField):
    """3-bit volume control for ringtone playback."""

    def __init__(self) -> None:
        super().__init__(0, 3)


class SensitivityField(BitField):
    """8-bit sensitivity"""

    def __init__(self) -> None:
        super().__init__(56, 8)


class TimeoutField(BitField):
    """8-bit timeout"""

    def __init__(self) -> None:
        super().__init__(48, 8)


class TriggerField(BitField):
    """8-bit trigger"""

    def __init__(self) -> None:
        super().__init__(40, 8)


class ChecksumField(BitField):
    """16-bit checksum"""

    def __init__(self) -> None:
        super().__init__(0, 16)

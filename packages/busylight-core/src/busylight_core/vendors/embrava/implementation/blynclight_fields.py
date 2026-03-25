"""Embrava Blynclight bit field definitions.

This module defines BitField classes used to construct device commands.
Each field represents a specific portion of the 48-bit command structure
that controls various aspects of Embrava Blynclight device behavior.
"""

from busylight_core.word import BitField


class RedField(BitField):
    """8-bit red color component."""

    def __init__(self) -> None:
        super().__init__(40, 8)


class BlueField(BitField):
    """8-bit blue color component."""

    def __init__(self) -> None:
        super().__init__(32, 8)


class GreenField(BitField):
    """8-bit green color component."""

    def __init__(self) -> None:
        super().__init__(24, 8)


class OffBit(BitField):
    """1-bit field to turn light off, clear to turn light on."""

    def __init__(self) -> None:
        super().__init__(17, 1)


class DimBit(BitField):
    """1-bit field to dim light, clear to brighten light."""

    def __init__(self) -> None:
        super().__init__(18, 1)


class FlashBit(BitField):
    """1-bit field to flash light, clear to stop flashing."""

    def __init__(self) -> None:
        super().__init__(19, 1)


class SpeedField(BitField):
    """3-bit field to set flash speed: 1=slow, 2=medium, 4=fast."""

    def __init__(self) -> None:
        super().__init__(20, 3)


class RepeatBit(BitField):
    """1-bit field to repeat sound, clear to play sound once."""

    def __init__(self) -> None:
        super().__init__(13, 1)


class PlayBit(BitField):
    """1-bit field to play sound, clear to stop sound."""

    def __init__(self) -> None:
        super().__init__(12, 1)


class MusicField(BitField):
    """4-bit field to select music to play, ranges from 0 to 15."""

    def __init__(self) -> None:
        super().__init__(8, 4)


class VolumeField(BitField):
    """4-bit field to set volume level, ranges from 0 to 15."""

    def __init__(self) -> None:
        super().__init__(0, 4)


class MuteBit(BitField):
    """1-bit field to mute sound, clear to enable sound."""

    def __init__(self) -> None:
        super().__init__(4, 1)

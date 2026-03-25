"""ThingM Blink(1) bit field definitions.

This module defines BitField classes used to construct device commands.
Each field represents a specific portion of the 64-bit command structure
that controls various aspects of ThingM Blink(1) device behavior.
"""

from busylight_core.word import BitField


class ReportField(BitField):
    """8-bit report field for HID communication."""

    def __init__(self) -> None:
        super().__init__(56, 8)


class ActionField(BitField):
    """8-bit action field specifying the command to execute."""

    def __init__(self) -> None:
        super().__init__(48, 8)


class RedField(BitField):
    """8-bit red color component."""

    def __init__(self) -> None:
        super().__init__(40, 8)


class GreenField(BitField):
    """8-bit green color component."""

    def __init__(self) -> None:
        super().__init__(32, 8)


class BlueField(BitField):
    """8-bit blue color component."""

    def __init__(self) -> None:
        super().__init__(24, 8)


class PlayField(BitField):
    """8-bit play field for pattern playback control."""

    def __init__(self) -> None:
        super().__init__(40, 8)


class StartField(BitField):
    """8-bit start field for pattern range specification."""

    def __init__(self) -> None:
        super().__init__(32, 8)


class StopField(BitField):
    """8-bit stop field for pattern range specification."""

    def __init__(self) -> None:
        super().__init__(24, 8)


class CountField(BitField):
    """8-bit count field for repetition control."""

    def __init__(self) -> None:
        super().__init__(16, 8)


class FadeField(BitField):
    """16-bit fade field for transition timing in milliseconds."""

    def __init__(self) -> None:
        super().__init__(8, 16)


class LedsField(BitField):
    """8-bit LED selection field for multi-LED devices."""

    def __init__(self) -> None:
        super().__init__(0, 8)


class LinesField(BitField):
    """8-bit line field for pattern line indexing."""

    def __init__(self) -> None:
        super().__init__(0, 8)

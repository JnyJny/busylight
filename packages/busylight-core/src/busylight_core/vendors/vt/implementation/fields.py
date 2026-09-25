"""VT DND bit field definitions.

This module defines BitField classes used to construct device commands.
Each field represents a specific portion of the 40-bit command structure.
"""

from busylight_core.word import BitField, ReadOnlyBitField


class ReportField(ReadOnlyBitField):
    """8-bit report field for HID communication, fixed at construction."""


class ActionField(BitField):
    """8-bit action field specifying the command to execute."""


class DataField(BitField):
    """8-bit command argument field, RGB components for SetColor."""

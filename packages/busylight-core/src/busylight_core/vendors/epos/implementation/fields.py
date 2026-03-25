"""EPOS Busylight bit field definitions.

This module defines BitField classes used to construct device commands.
Each field represents a specific portion of the 80-bit command structure
that controls various aspects of EPOS Busylight device behavior.
"""

from busylight_core.word import BitField


class ReportField(BitField):
    """8-bit report field for HID communication."""


class ActionField(BitField):
    """16-bit action field specifying the command to execute."""


class ColorField(BitField):
    """8-bit color component field for RGB values."""


class OnField(BitField):
    """8-bit field that controls the device power state."""

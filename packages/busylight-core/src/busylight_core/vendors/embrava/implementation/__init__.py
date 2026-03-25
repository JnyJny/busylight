"""Embrava device implementation details."""

from .blynclight_enums import BlynclightFlashSpeed
from .blynclight_fields import (
    BlueField,
    DimBit,
    FlashBit,
    GreenField,
    MusicField,
    MuteBit,
    OffBit,
    PlayBit,
    RedField,
    RepeatBit,
    SpeedField,
    VolumeField,
)
from .blynclight_state import BlynclightState
from .blyncusb_colors import (
    BLYNCUSB_COLOR_TO_RGB,
    BlyncusbColor,
    rgb_to_blyncusb_color,
    snap_color,
)
from .blyncusb_enums import BLYNCUSB_TO_TENX20, Tenx20Color

# Backward-compatible aliases
FlashSpeed = BlynclightFlashSpeed
State = BlynclightState

__all__ = [
    "BLYNCUSB_COLOR_TO_RGB",
    "BLYNCUSB_TO_TENX20",
    "BlueField",
    "BlynclightFlashSpeed",
    "BlynclightState",
    "BlyncusbColor",
    "DimBit",
    "FlashBit",
    "FlashSpeed",
    "GreenField",
    "MusicField",
    "MuteBit",
    "OffBit",
    "PlayBit",
    "RedField",
    "RepeatBit",
    "SpeedField",
    "State",
    "Tenx20Color",
    "VolumeField",
    "rgb_to_blyncusb_color",
    "snap_color",
]

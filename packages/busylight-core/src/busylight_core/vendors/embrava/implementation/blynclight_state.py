"""Embrava Blynclight device state management.

This module defines the State class that manages the complete command
structure for Embrava Blynclight devices, including LED control and
audio functionality.
"""

from busylight_core.word import Word

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


class BlynclightState(Word):
    """Complete device state for Embrava Blynclight commands.

    The State class manages the full command structure sent to Embrava devices.
    It controls both LED behavior (color, brightness, flashing) and audio
    functionality (ringtones, volume, playback control). The state is
    serialized to bytes for transmission to the hardware.
    """

    def __init__(self) -> None:
        super().__init__(0, 48)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(0x{self!s})"

    def __str__(self) -> str:
        """Return a human-readable representation of the device state."""
        fields = [
            f"red:    {self.red:#04x}",
            f"blue:   {self.blue:#04x}",
            f"green:  {self.green:#04x}",
            f"off:    {self.off}",
            f"dim:    {self.dim}",
            f"flash:  {self.flash}",
            f"speed:  {self.speed}",
            f"repeat: {self.repeat}",
            f"play:   {self.play}",
            f"music:  {self.music}",
            f"volume: {self.volume}",
            f"mute:   {self.mute}",
        ]
        return "\n".join(fields)

    def reset(self) -> None:
        """Reset the state to default values.

        Sets the device to off state with no audio playback and
        default flash speed settings.
        """
        self.red = 0
        self.blue = 0
        self.green = 0
        self.off = True
        self.dim = False
        self.flash = False
        self.speed = BlynclightFlashSpeed.slow.value
        self.play = False
        self.mute = False
        self.repeat = False
        self.music = 0
        self.volume = 0

    red = RedField()
    blue = BlueField()
    green = GreenField()
    off = OffBit()
    dim = DimBit()
    flash = FlashBit()
    speed = SpeedField()
    repeat = RepeatBit()
    play = PlayBit()
    music = MusicField()
    volume = VolumeField()
    mute = MuteBit()

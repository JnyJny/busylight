"""Embrava Blynclight Plus Support"""

from typing import ClassVar

from .blynclight_base import BlynclightBase


class BlynclightPlus(BlynclightBase):
    """Embrava Blynclight Plus status light controller.

    An enhanced version of the Blynclight with additional features
    while maintaining the same basic functionality.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x2C0D, 0x0002): "Blynclight Plus",
        (0x2C0D, 0x0010): "Blynclight Plus",
    }

    def play_sound(self, music: int = 0, volume: int = 1, repeat: bool = False) -> None:
        """Play a sound on the device.

        :param music: Music track number to play (0-7)
        :param volume: Volume level (0-3)
        :param repeat: Whether the music repeats
        """
        with self.batch_update():
            self.state.repeat = repeat
            self.state.play = True
            self.state.music = music
            self.state.mute = False
            self.state.volume = volume

    def stop_sound(self) -> None:
        """Stop playing any currently playing sound."""
        with self.batch_update():
            self.state.play = False

    def mute(self) -> None:
        """Mute the device sound output."""
        with self.batch_update():
            self.state.mute = True

    def unmute(self) -> None:
        """Unmute the device sound output."""
        with self.batch_update():
            self.state.mute = False

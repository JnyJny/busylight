"""Blynclight USB protocol mixins.

Provides the state machine, packet format, and control methods shared
by Embrava Blynclight devices and OEM variants (e.g. Plantronics).

Two mixins at different capability levels:

- **BlynclightProtocol**: core protocol shared by all Blynclight
  devices. State management, packet serialization, color, on/off,
  dim/bright, flash patterns, reset.

- **BlynclightPlusProtocol**: extends BlynclightProtocol with sound
  playback, mute, and volume control. Used by BlynclightPlus and
  OEM equivalents like Plantronics StatusIndicator.

Concrete classes provide vendor identity and supported_device_ids.
"""

from functools import cached_property

from .implementation import BlynclightFlashSpeed, BlynclightState


class BlynclightProtocol:
    """Mixin providing the core Blynclight USB protocol.

    Implements state management, packet serialization, color control,
    on/off with off-bit management, dim/bright, flash patterns, and
    device reset. Used by all Blynclight family devices.

    Example::

        class MyLight(MyVendorBase, BlynclightProtocol):
            supported_device_ids = {(0xAAAA, 0xBBBB): "My Light"}
    """

    @cached_property
    def state(self) -> "BlynclightState":
        """The device state manager."""
        return BlynclightState()

    def __bytes__(self) -> bytes:
        """Return the device state as bytes for USB communication."""
        return bytes([0, *bytes(self.state), 0xFF, 0x22])

    @property
    def color(self) -> tuple[int, int, int]:
        """Tuple of RGB color values."""
        return (self.state.red, self.state.green, self.state.blue)

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        """Set the RGB color values."""
        self.state.red, self.state.green, self.state.blue = value

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on the device with the specified color.

        :param color: RGB color tuple (red, green, blue)
        :param led: LED index (not used by Blynclight devices)
        """
        with self.batch_update():
            self.color = color
            if not self.is_lit:
                self.state.off = True
                self.state.dim = False
                self.state.flash = False
            else:
                self.state.off = False

    def dim(self) -> None:
        """Dim the current light color."""
        with self.batch_update():
            self.state.dim = True

    def bright(self) -> None:
        """Restore the light to full brightness."""
        with self.batch_update():
            self.state.dim = False

    def flash(
        self,
        color: tuple[int, int, int],
        speed: BlynclightFlashSpeed | None = None,
    ) -> None:
        """Start flashing pattern with specified color and timing.

        :param color: RGB color tuple for flash pattern
        :param speed: Flash timing rate (defaults to slow if not specified)
        """
        speed = speed or BlynclightFlashSpeed.slow

        with self.batch_update():
            self.color = color
            self.state.flash = True
            self.state.speed = speed.value

    def stop_flashing(self) -> None:
        """Stop the flashing pattern and return to solid color."""
        with self.batch_update():
            self.state.flash = False

    def reset(self) -> None:
        """Reset the device to its default state (off, no sound)."""
        self.state.reset()
        self.update()


class BlynclightPlusProtocol(BlynclightProtocol):
    """Mixin extending BlynclightProtocol with sound capabilities.

    Adds sound playback, mute, and volume control on top of the core
    protocol. Used by BlynclightPlus and OEM equivalents like the
    Plantronics StatusIndicator.

    Example::

        class MyOEMLight(MyVendorBase, BlynclightPlusProtocol):
            supported_device_ids = {(0xAAAA, 0xBBBB): "My Light"}
    """

    def play_sound(
        self,
        music: int = 0,
        volume: int = 1,
        repeat: bool = False,
    ) -> None:
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

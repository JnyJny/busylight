"""Embrava Blynclight family base class."""

from functools import cached_property

from .embrava_base import EmbravaBase
from .implementation import BlynclightFlashSpeed, BlynclightState


class BlynclightBase(EmbravaBase):
    """Base class for Embrava Blynclight family devices.

    Provides common functionality for all Blynclight devices including
    sound playback, volume control, dim/bright control, and flash patterns.
    """

    @cached_property
    def state(self) -> "BlynclightState":
        """The device state manager."""
        return BlynclightState()

    def __bytes__(self) -> bytes:
        """Return the device state as bytes for USB communication."""
        if not self.is_lit:
            self.state.off = True
            self.state.flash = False
            self.state.dim = False

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

        Activates the device's built-in flash pattern with the given
        color and speed. The device will alternate between the color
        and off state at the specified rate.

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

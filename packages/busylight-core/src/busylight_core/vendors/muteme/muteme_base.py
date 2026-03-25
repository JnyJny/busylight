"""MuteMe family base class."""

import struct
from functools import cached_property

from busylight_core.light import Light

from .implementation import State


class MuteMeBase(Light):
    """Base class for MuteMe family devices.

    Provides common functionality for all MuteMe devices including
    button support, device detection, and simple RGB control.
    Use this as a base class when implementing new MuteMe variants.
    """

    @staticmethod
    def vendor() -> str:
        """Return the vendor name for MuteMe devices.

        Provides the official vendor branding for user interfaces
        and device identification.

        :return: Official vendor name string
        """
        return "MuteMe"

    @cached_property
    def state(self) -> "State":
        """Device state manager for controlling light behavior.

        Returns a State instance that manages RGB color values and
        other device-specific properties. Use this to modify device
        state before calling update() to apply changes.

        :return: State instance for managing device properties
        """
        return State()

    @cached_property
    def struct(self) -> struct.Struct:
        """The binary struct formatter for device communication."""
        return struct.Struct("!xB")

    def __bytes__(self) -> bytes:
        """Return the device state as bytes for USB communication."""
        return self.struct.pack(self.state.value)

    @property
    def color(self) -> tuple[int, int, int]:
        """Tuple of RGB color values."""
        return self.state.color

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        """Set the RGB color values."""
        self.state.color = value

    @property
    def is_pluggedin(self) -> bool:
        """True if the device is plugged in and responsive."""
        # EJO No reason for eight, just a power of two.
        try:
            nbytes = self.hardware.send_feature_report([0] * 8)
        except ValueError:
            pass
        else:
            return nbytes == 8
        return False

    @property
    def is_button(self) -> bool:
        """True if this device has button functionality."""
        return True

    @property
    def button_on(self) -> bool:
        """True if the mute button is currently pressed."""
        raise NotImplementedError

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on the device with the specified color.

        :param color: RGB color tuple (red, green, blue) with values 0-255
        :param led: LED index (unused for MuteMe devices)
        """
        with self.batch_update():
            self.color = color

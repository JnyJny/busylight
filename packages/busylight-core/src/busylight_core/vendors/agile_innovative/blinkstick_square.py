"""Agile Innovative Blinkstick Square implementation details."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from busylight_core.hardware import Hardware

from .blinkstick_base import BlinkStickBase
from .implementation import State


class BlinkStickSquare(BlinkStickBase):
    """Agile Innovative BlinkStick Square status light controller.

    The BlinkStick Square is a USB-connected RGB LED device with a square form factor
    that can be controlled to display various colors and patterns for status indication.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x20A0, 0x41E5): "BlinkStick Square",
    }

    @classmethod
    def claims(cls, hardware: Hardware) -> bool:
        """Return True if the hardware describes a BlinkStick Square."""
        if not super().claims(hardware):
            return False
        try:
            major, _ = cls.get_version(hardware.serial_number)
        except ValueError:
            return False
        return major == 3 and hardware.release_number == 0x200

    @cached_property
    def state(self) -> State:
        """The state of the BlinkStick Square."""
        return State.blinkstick_square()

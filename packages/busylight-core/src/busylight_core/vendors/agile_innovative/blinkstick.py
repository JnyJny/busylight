"""Agile Innovative BlinkStick"""

from functools import cached_property
from typing import ClassVar

from busylight_core import Hardware

from .blinkstick_base import BlinkStickBase
from .implementation import State


class BlinkStick(BlinkStickBase):
    """Agile Innovative BlinkStick USB RGB LED controller.

    The original BlinkStick is a simple USB-connected RGB LED device
    for basic status indication. Use this class to control the original
    BlinkStick hardware for simple color display and status signaling.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x20A0, 0x41E5): "BlinkStick",
    }

    @classmethod
    def claims(cls, hardware: Hardware) -> bool:
        """Check if hardware is an original BlinkStick device.

        Verifies USB IDs and firmware version to distinguish the original
        BlinkStick from newer variants with extended capabilities.

        :param hardware: Hardware instance to test for compatibility
        :return: True if hardware is an original BlinkStick
        """
        if not super().claims(hardware):
            return False
        try:
            major, _ = cls.get_version(hardware.serial_number)
        except ValueError:
            return False
        return major == 1

    @cached_property
    def state(self) -> State:
        """Get the current state of the BlinkStick."""
        return State.blinkstick()

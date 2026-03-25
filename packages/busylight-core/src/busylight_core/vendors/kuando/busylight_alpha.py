"""Busylight Alpha Support"""

from typing import ClassVar

from .busylight_base import BusylightBase


class BusylightAlpha(BusylightBase):
    """Kuando Busylight Alpha status light controller.

    The Busylight Alpha is a USB-connected RGB LED device that requires
    periodic keepalive messages to maintain its connection state.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x04D8, 0xF848): "Busylight Alpha",
        (0x27BB, 0x3BCA): "Busylight Alpha",
        (0x27BB, 0x3BCB): "Busylight Alpha",
        (0x27BB, 0x3BCE): "Busylight Alpha",
    }

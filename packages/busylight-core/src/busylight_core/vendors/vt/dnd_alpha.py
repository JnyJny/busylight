"""VT DND Alpha Support"""

from typing import ClassVar

from .dnd_base import DNDBase


class DNDAlpha(DNDBase):
    """VT DND Alpha status light controller.

    The DND Alpha is a USB-connected RGB LED device with three
    brightness levels and two firmware flash patterns.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x340B, 0xF002): "DND Alpha",
    }

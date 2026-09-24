"""VT DND Omega Support"""

from typing import ClassVar

from .dnd_base import DNDBase


class DNDOmega(DNDBase):
    """VT DND Omega status light controller.

    The DND Omega shares the DND Alpha's command protocol and features.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x340B, 0xF001): "DND Omega",
    }

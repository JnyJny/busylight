"""Embrava Blynclight Plus Support"""

from typing import ClassVar

from .blynclight_protocol import BlynclightPlusProtocol
from .embrava_base import EmbravaBase


class BlynclightPlus(BlynclightPlusProtocol, EmbravaBase):
    """Embrava Blynclight Plus status light controller.

    Combines Embrava vendor identity with the full Blynclight Plus
    protocol, including sound playback, mute, and volume control.
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x2C0D, 0x0002): "Blynclight Plus",
        (0x2C0D, 0x0010): "Blynclight Plus",
    }

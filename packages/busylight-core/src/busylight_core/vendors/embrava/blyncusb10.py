"""Embrava Blynclight BLYNCUSB10 Support (VID 0x1130, PID 0x0001/0x0002)

Early Blynclight using the blynux 8-byte USB feature report protocol.
Supports 7 predefined colors plus OFF.

Protocol source: https://github.com/ticapix/blynux

Command format:
- Bytes 0-6: Header (0x55, 0x53, 0x42, 0x43, 0x00, 0x40, 0x02)
- Byte 7: (color_mask << 4) | 0x0F
"""

from collections.abc import Callable
from typing import ClassVar

from .blyncusb_base import BlyncusbBase
from .implementation import rgb_to_blyncusb_color


class Blyncusb10(BlyncusbBase):
    """Embrava Blynclight BLYNCUSB10 (PID 0x0001, 0x0002) USB status light.

    Uses the blynux 8-byte USB control transfer protocol. Supports 7
    predefined colors plus off. No audio, flash, or dim capability.

    Device specifications:
    - VID: 0x1130
    - PID: 0x0001 or 0x0002
    - Interface: 1
    - Protocol: 8-byte USB HID feature report (blynux)
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x1130, 0x0001): "Blynclight BLYNCUSB10",
        (0x1130, 0x0002): "Blynclight BLYNCUSB10",
    }

    def __bytes__(self) -> bytes:
        """Return the device state as bytes for USB communication.

        Command format: 7 header bytes + 1 color byte.
        Color byte: (color_mask << 4) | 0x0F
        """
        blyncusb_color = rgb_to_blyncusb_color(*self.color)
        color_byte = (blyncusb_color.value << 4) | 0x0F
        return bytes([0x55, 0x53, 0x42, 0x43, 0x00, 0x40, 0x02, color_byte])

    @property
    def write_strategy(self) -> Callable[[bytes], None]:
        """The write method used by this light.

        The BLYNCUSB10 uses send_feature_report for USB control transfers.
        """
        return self.hardware.handle.send_feature_report

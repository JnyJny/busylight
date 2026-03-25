"""Embrava Blynclight BLYNCUSB20 Support (VID 0x1130, PID 0x1E00)

Early Blynclight using the TENX20 chipset with a 2-step HID write protocol.
Supports 7 predefined colors plus OFF.

Protocol source: decompiled Blynclight.dll SDK

Command format:
- 65-byte HID write on interface 1
- Byte 0: Report ID (0x00)
- Byte 1: Control code
- Bytes 2-64: Padding (0x00)

The TENX20 requires a two-step sequence: reset (0x73), then color code.
This is handled via write_strategy so the base Light.update() method
retains exclusive access and platform handling.
"""

from collections.abc import Callable
from typing import ClassVar

from .blyncusb_base import BlyncusbBase
from .implementation import BLYNCUSB_TO_TENX20, Tenx20Color, rgb_to_blyncusb_color


class Blyncusb20(BlyncusbBase):
    """Embrava Blynclight BLYNCUSB20 (PID 0x1E00) USB status light.

    Uses the TENX20 chipset with a two-step HID write protocol:
    1. Send 0x73 (reset/prepare)
    2. Send color code

    The two-step sequence is encapsulated in write_strategy so that
    Light.update() handles exclusive access and platform specifics
    without modification.

    Device specifications:
    - VID: 0x1130
    - PID: 0x1E00
    - Interface: 1
    - Protocol: TENX20 (65-byte HID write, 2-step command)
    - Colors: 7 predefined + OFF
    """

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x1130, 0x1E00): "Blynclight BLYNCUSB20",
    }

    RESET_CODE: ClassVar[int] = 0x73
    BUFFER_SIZE: ClassVar[int] = 65

    def __bytes__(self) -> bytes:
        """Return the color command as bytes for USB communication.

        Returns only the color-setting command (step 2). The reset
        command (step 1) is handled by write_strategy.
        """
        blyncusb_color = rgb_to_blyncusb_color(*self.color)
        tenx20_color = BLYNCUSB_TO_TENX20.get(blyncusb_color, Tenx20Color.OFF)
        return bytes([0x00, tenx20_color] + [0x00] * 63)

    @property
    def write_strategy(self) -> Callable[[bytes], None]:
        """Write strategy that implements the TENX20 two-step protocol.

        Sends the reset command (0x73) before writing the color command.
        This keeps the two-step protocol private to the device
        implementation without overriding Light.update().
        """
        handle = self.hardware.handle
        reset_command = bytes([0x00, self.RESET_CODE] + [0x00] * 63)

        def tenx20_write(color_command: bytes) -> None:
            handle.write(reset_command)
            handle.write(color_command)

        return tenx20_write

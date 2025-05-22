"""
"""

from typing import Dict, Tuple

from loguru import logger

from ..seriallight import SerialLight


class MuteSync(SerialLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x10C4, 0xEA60): "MuteSync Button",
        }

    @staticmethod
    def vendor() -> str:
        return "MuteSync"

    @classmethod
    def claims(cls, light_info: dict) -> bool:
        """Returns True if the light_info describes a MuteSync Button."""

        # Addresses issue #356 where MuteSync claims another device with
        # a SiliconLabs CP2102 USB to Serial controller that is not a MuteSync
        # device.

        claim = super().claims(light_info)

        product = cls.vendor().lower() in light_info.get("product_string", "").lower()

        return claim and product

    def __bytes__(self) -> bytes:

        buf = [65] + [*self.color] * 4

        return bytes(buf)

    @property
    def is_button(self) -> bool:
        return True

    @property
    def button_on(self) -> bool:
        return False

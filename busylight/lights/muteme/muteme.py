""" MuteMe Button & Light
"""

from typing import Dict, Tuple

from loguru import logger

from ..hidlight import HIDLight
from ..light import LightInfo

from ._muteme import Command


class MuteMe(HIDLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x16C0, 0x27DB): "MuteMe Original",
            (0x20A0, 0x42DA): "MuteMe Original",
        }

    @staticmethod
    def vendor() -> str:
        return "MuteMe"

    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:
        self.command = Command()
        super().__init__(light_info, reset=reset, exclusive=exclusive)

    def __bytes__(self) -> bytes:

        return self.command.bytes

    def on(self, color: Tuple[int, int, int]) -> None:

        with self.batch_update():
            self.command.color = color

    def reset(self) -> None:

        with self.batch_update():
            self.command.reset()

    @property
    def is_pluggedin(self) -> bool:

        # EJO No reason for eight, just a power of two.
        try:
            nbytes = self.device.send_feature_report([0] * 8)
            return nbytes == 8
        except ValueError:
            pass
        return False

    @property
    def is_button(self) -> bool:
        return True

    @property
    def button_on(self) -> bool:
        raise NotImplementedError()

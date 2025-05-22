""" Busylight Alpha Support
"""

import asyncio

from typing import Dict, Tuple, Union

from loguru import logger

from ..hidlight import HIDLight
from ..light import LightInfo

from ._busylight import CommandBuffer, Instruction


class Busylight_Alpha(HIDLight):
    @staticmethod
    def supported_device_ids() -> Dict[Tuple[int, int], str]:
        return {
            (0x04D8, 0xF848): "Busylight Alpha",
            (0x27BB, 0x3BCA): "Busylight Alpha",
            (0x27BB, 0x3BCB): "Busylight Alpha",
            (0x27BB, 0x3BCE): "Busylight Alpha",
        }

    @staticmethod
    def vendor() -> str:
        return "Kuando"

    def __init__(
        self,
        light_info: LightInfo,
        reset: bool = True,
        exclusive: bool = True,
    ) -> None:

        self.command: CommandBuffer = CommandBuffer()
        super().__init__(light_info, reset=reset, exclusive=exclusive)

    def __bytes__(self) -> bytes:

        return bytes(self.command)

    def on(self, color: Tuple[int, int, int]) -> None:

        with self.batch_update():
            self.color = color
            instruction = Instruction.Jump(target=0, color=color, on_time=0, off_time=0)
            self.command.line0 = instruction.value

        self.add_task("keepalive", _keepalive)

    def off(self) -> None:

        with self.batch_update():
            self.color = (0, 0, 0)
            instruction = Instruction.Jump(
                target=0, color=self.color, on_time=0, off_time=0
            )
            self.command.line0 = instruction.value


async def _keepalive(light: Busylight_Alpha, interval: int = 0xF) -> None:
    """Send a Keepalive packet to a Busylight."""

    interval = interval & 0x0F
    sleep_interval = round(interval / 2)
    command = Instruction.KeepAlive(interval).value

    while True:
        with light.batch_update():
            light.command.line0 = command
        await asyncio.sleep(sleep_interval)

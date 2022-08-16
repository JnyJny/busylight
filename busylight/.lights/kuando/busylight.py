""" Kuando BusyLight Family
"""
import asyncio

from typing import Awaitable, Optional

from ...color import ColorTuple

from ..speed import Speed
from ..usblight import USBLight, HidInfo

from .busylight_impl import CommandBuffer, Instruction


async def keepalive(light: USBLight, interval: int = 0xF) -> None:
    """Async coroutine for delivering a keepalive packet to the device.

    The coroutine sends a KeepAlive packet to the device every:

    By default, the KeepAlive packet is configured to timeout in
    15 seconds and sleeps for 14 seconds. We are counting on the
    coroutine being scheduled to run by the asyncio event loop in
    that next second.

    :interval: 4-bit integer value in seconds
    """

    interval = interval & 0x0F
    sleep_interval = round(interval / 2)
    ka_value = Instruction.KeepAlive(interval).value

    while True:
        with light.batch_update():
            light.command.line0 = ka_value
        await asyncio.sleep(sleep_interval)


class Busylight(USBLight):

    SUPPORTED_DEVICE_IDS = {
        (0x04D8, 0xF848): "Busylight Alpha",
        (0x27BB, 0x3BCA): "Busylight Alpha",
        (0x27BB, 0x3BCD): "Busylight Omega",
        (0x27BB, 0x3BCF): "Busylight Omega",
    }

    vendor = "Kuando"

    def __init__(
        self,
        hidinfo: HidInfo,
        reset: bool = True,
    ) -> None:
        self.command = CommandBuffer()
        super().__init__(hidinfo, reset=reset)

    @property
    def name(self) -> str:
        return self.SUPPORTED_DEVICE_IDS[(self.vendor_id, self.product_id)]

    def __bytes__(self) -> bytes:
        return bytes(self.command)

    def on(self, color: ColorTuple) -> None:

        with self.batch_update():
            super().on(color)
            instruction = Instruction.Jump(
                target=0,
                color=color,
                on_time=0,
                off_time=0,
            )
            self.command.line0 = instruction.value
        self.add_task("keepalive", keepalive)

    def blink(
        self, color: ColorTuple, blink: Speed = Speed.Slow
    ) -> Optional[Awaitable]:
        dc = 10 // blink.rate
        with self.batch_update():
            instruction = Instruction.Jump(
                target=0,
                color=color,
                on_time=dc,
                off_time=dc,
            )
            self.command.line0 = instruction.value
        self.add_task("keepalive", keepalive)

    def off(self) -> None:

        color = (0, 0, 0)
        super().on(color)
        with self.batch_update():
            instruction = Instruction.Jump(
                target=0,
                color=color,
                on_time=0,
                off_time=0,
            )
            self.command.line0 = instruction.value
        super().off()

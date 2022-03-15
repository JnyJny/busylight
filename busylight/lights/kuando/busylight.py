""" Kuando BusyLight Family
"""
import asyncio

from typing import Awaitable, Optional

from loguru import logger

from ..color import ColorTuple
from ..speed import Speed
from ..usblight import USBLight, HidInfo

from .busylight_impl import CommandBuffer, Instruction


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

    def start_keepalive(self) -> bool:
        """"""
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            return False
        logger.debug(f"{self.name} adding keepalive to event loop")
        loop.create_task(self.keepalive())
        return True

    def on(self, color: ColorTuple) -> Optional[Awaitable]:

        with self.batch_update():
            super().on(color)
            instruction = Instruction.Jump(
                target=0,
                color=color,
                on_time=0,
                off_time=0,
            )
            self.command.line0 = instruction.value
        return self.keepalive

    def blink(
        self, color: ColorTuple, blink: Speed = Speed.Stop
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
        return self.keepalive

    def off(self) -> None:
        self.on((0, 0, 0))

    async def keepalive(self, interval: int = 0xF) -> None:
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
        # EJO min/max range checking on sleep_interval here?
        ka_value = Instruction.KeepAlive(interval).value

        while True:
            logger.debug(
                f"{self.name} keepalive for {interval}s, sleeping {sleep_interval}s"
            )
            with self.batch_update():
                self.command.line0 = ka_value
            await asyncio.sleep(sleep_interval)

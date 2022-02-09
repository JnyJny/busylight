"""Support for Kuando Busylights
"""

from time import sleep
from typing import Generator, List, Tuple, Union

from loguru import logger

from ..thread import CancellableThread
from ..usblight import USBLight, USBLightIOError
from .hardware import BusylightState, Jump, KeepAlive


class Busylight(USBLight):

    VENDOR_IDS: List[int] = [0x27BB, 0x04D8]
    PRODUCT_IDS: List[int] = [
        0xF848,  # UC Busylight Alpha
        0x3BCD,  # UC Busylight Omega
    ]
    vendor = "Kuando"

    @property
    def state(self) -> BusylightState:
        """Implementation dependent hardware state."""
        try:
            return self._state
        except AttributeError:
            pass
        self._state: BusylightState = BusylightState()
        return self._state

    def __bytes__(self) -> bytes:
        return bytes(self.state)

    def reset(self) -> None:
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        super().on(color)

        instruction = Jump(0)
        instruction.color = color

        with self.batch_update():
            self.reset()
            self.state.line0 = instruction.value

    def blink(self, color: Tuple[int, int, int], speed: int = 1) -> None:

        super().blink(color, speed)

        instruction = Jump(0)
        instruction.color = color  # type: ignore
        instruction.repeat = 0  # type: ignore
        instruction.dc_on = 10 // speed  # type: ignore
        instruction.dc_off = 10 // speed  # type: ignore

        with self.batch_update():
            self.reset()
            self.state.line0 = instruction.value

    def keepalive(self) -> Generator[float, None, None]:
        """Sends a keep alive command to the device periodically.

        This device requires constant reassurance and encouragement.
        """

        ## This method is "tuned" to send a keep alive message to the device
        ## every 7.5 seconds, which is half of the device's maximum 15 second
        ## keep alive window. My goal is to reduce the amount of writes to the
        ## USB subsystem which are "noops" but have enough margin that drift
        ## due to process scheduling doesn't cause the the keep alive to be
        ## sent late. I cannot imagine 7.5s of drift but weirder things have
        ## happened.
        ##
        ## This would be fine by itself, however when a light is released via
        ## the "release" method, the keep alive thread is cancelled.  Since
        ## the thread is asleep for aeons of time (7.5s) the release method
        ## will necessarily have a maximum latency of 7.5s before returning.
        ##
        ## To avoid this unresponsiveness, the keep alive generator has
        ## bookkeeping that sends a packet every 7.5 seconds but sleeps
        ## for a much shorter interval (0.1 seconds). While 0.1s latency
        ## is still a "long time" for computers, it's much less noticible
        ## by humans.
        ##
        ## I'm not thrilled about this busy-waiting burning up CPU to avoid
        ## a perceived performance problem for an infrequently called
        ## method, but this seems to be the least bad solution so far.

        timeout = 0xF
        interval = 0.1
        ka = KeepAlive(timeout).value
        logger.info(f"keepalive generator {ka:x}, {timeout} s {interval:5.3f}")
        countdown = timeout / 2

        while True:
            if countdown <= 0:
                try:
                    with self.batch_update():
                        logger.info("keepalive sent")
                        self.state.reset()
                        self.state.line0 = ka
                except USBLightIOError as error:
                    logger.error("{self} error {error}")
                    break
                countdown = timeout / 2
            else:
                countdown -= interval

            yield interval

        logger.info("keepalive generator returning")

    @property
    def keepalive_thread(self) -> CancellableThread:
        """A CancellableThread running the `keepalive` method."""
        try:
            return self._keepalive_thread
        except AttributeError:
            pass
        self._keepalive_thread: CancellableThread = CancellableThread(
            self.keepalive(), f"keepalive-{self.identifier}"
        )
        return self._keepalive_thread

    @property
    def is_animating(self) -> bool:
        for thrd in [self.animation_thread, self.keepalive_thread]:
            if thrd and thrd.is_alive():
                return True
        return False

    def acquire(self, reset: bool) -> None:
        with self.lock:
            super().acquire(reset)
            self.keepalive_thread.start()

    def release(self) -> None:
        with self.lock:
            try:
                self.keepalive_thread.cancel()
                while self.keepalive_thread.alive:
                    self.keepalive_thread.join(15)
                del self._keepalive_thread

            except Exception as error:
                logger.error(f"{error}")

            super().release()

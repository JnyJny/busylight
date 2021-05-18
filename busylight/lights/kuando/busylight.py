"""Support for Kuando Busylights
"""

from time import sleep
from typing import Generator, List, Tuple, Union

from loguru import logger

from .hardware import BusyLightState
from .hardware import Jump
from .hardware import KeepAlive

from ..thread import CancellableThread
from ..usblight import USBLight
from ..usblight import USBLightIOError


class BusyLight(USBLight):

    VENDOR_IDS: List[int] = [0x27BB]
    PRODUCT_IDS: List[int] = []
    vendor = "Kuando"

    @property
    def state(self) -> BusyLightState:
        """Implementation dependent hardware state."""
        try:
            return self._state
        except AttributeError:
            pass
        self._state: BusyLightState = BusyLightState()
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

    def keepalive(self) -> Generator[float, None, bool]:
        """Sends a keep alive command to the device periodically.

        This device requires constant reassurance and encouragement.
        """
        timeout = 0xF
        interval = timeout / 2
        ka = KeepAlive(timeout).value
        logger.info("keepalive generator initialized")
        while True:
            try:
                with self.batch_update():
                    self.state.reset()
                    self.state.line0 = ka
            except USBLightIOError as error:
                logger.error("{self} error {error}")
                break
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
    def is_animating(self):
        try:
            return self.animation_thread.is_alive()
        except Exception as error:
            logger.error(f"{self} is_animating: {error}")
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

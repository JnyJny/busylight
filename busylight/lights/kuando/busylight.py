"""Support for Kuando Busylights
"""

from time import sleep
from typing import Tuple

from .hardware import BusyLightState
from .hardware import InstructionJump as JumpTo
from .hardware import InstructionKeepAlive as KeepAlive

from ..thread import CancellableThread
from ..usblight import USBLight
from ..usblight import USBLightIOError


class BusyLight(USBLight):

    VENDOR_IDS = [0x27BB]
    PRODUCT_IDS = []
    vendor = "Kuando"

    @property
    def state(self):
        try:
            return self._state
        except AttributeError:
            pass
        self._state = BusyLightState()
        return self._state

    def reset(self) -> None:
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        self.color = color

        instruction = JumpTo(0)
        instruction.color = color
        instruction.repeat = 0xFF

        with self.batch_update():
            self.reset()
            self.state.line0 = instruction.value

    def off(self):

        self.on((0, 0, 0))

    def blink(self, color: Tuple[int, int, int], speed: int = 0) -> None:

        instruction = JumpTo(0)
        instruction.color = color
        instruction.repeat = 1
        instruction.dc_on = 10 // speed
        instruction.dc_off = 10 // speed

        with self.batch_update():
            self.reset()
            self.state.line0 = instruction.value

    def helper(self) -> None:

        timeout = 0xF
        interval = timeout // 2
        keepalive = KeepAlive(timeout).value

        while True:
            try:
                with self.batch_update():
                    self.state.line0 = keepalive
            except USBLightIOError:
                break
            yield
            sleep(interval)

    @property
    def helper_thread(self) -> CancellableThread:
        try:
            return self._helper_thread
        except AttributeError:
            pass
        self._helper_thread = CancellableThread(
            self.helper(), f"helper-{self.identifier}"
        )
        return self._helper_thread

    def acquire(self, reset: bool) -> None:

        with self.lock:
            super().acquire(reset)
            self.helper_thread.start()

    def release(self) -> None:
        with self.lock:
            try:
                self.helper_thread.cancel()
                del self._helper_thread
            except:
                pass
            super().release()

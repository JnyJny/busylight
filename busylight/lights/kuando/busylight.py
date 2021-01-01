"""Support for Kuando Busylights
"""

from time import sleep
from typing import Tuple, Union

from .hardware import BusyLightState
from .hardware import Jump
from .hardware import KeepAlive

from ..thread import CancellableThread
from ..usblight import USBLight
from ..usblight import USBLightIOError


class BusyLight(USBLight):

    VENDOR_IDS = [0x27BB]
    PRODUCT_IDS = []
    vendor = "Kuando"

    @property
    def state(self):
        """Implementation dependent hardware state."""
        try:
            return self._state
        except AttributeError:
            pass
        self._state = BusyLightState()
        return self._state

    def __bytes__(self):
        return bytes(self.state)

    def reset(self) -> None:
        self.state.reset()

    def on(self, color: Tuple[int, int, int]) -> None:

        super().on(color)

        instruction = Jump(0)
        instruction.color = color
        instruction.repeat = 0xFF

        with self.batch_update():
            self.reset()
            self.state.line0 = instruction.value

    def blink(self, color: Tuple[int, int, int], speed: int = 1) -> None:

        super().blink(color, speed)

        instruction = Jump(0)
        instruction.color = color
        instruction.repeat = 1
        instruction.dc_on = 10 // speed
        instruction.dc_off = 10 // speed

        with self.batch_update():
            self.reset()
            self.state.line0 = instruction.value

    def keepalive(self) -> None:
        """Sends a keep alive command to the device periodically.

        This device requires constant reassurance and encouragement.
        """
        timeout = 0xF
        interval = timeout // 2
        ka = KeepAlive(timeout).value
        while True:
            try:
                with self.batch_update():
                    self.state.reset()
                    self.state.line0 = ka
            except USBLightIOError:
                break
            yield
            sleep(interval)

    @property
    def keepalive_thread(self) -> CancellableThread:
        """A CancellableThread running the `keepalive` method."""
        try:
            return self._keepalive_thread
        except AttributeError:
            pass
        self._keepalive_thread = CancellableThread(
            self.keepalive(), f"keepalive-{self.identifier}"
        )
        return self._keepalive_thread

    @property
    def is_animating(self):
        return True

    def acquire(self, reset: bool) -> None:

        with self.lock:
            super().acquire(reset)
            self.keepalive_thread.start()

    def release(self) -> None:
        with self.lock:
            try:
                self.keepalive_thread.cancel()
                del self._keepalive_thread
            except:
                pass
            super().release()

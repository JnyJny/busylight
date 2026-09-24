"""VT DND Base Implementation"""

import asyncio
from collections.abc import Callable
from functools import cached_property
from time import sleep

from busylight_core.mixins import ColorableMixin

from .implementation import Brightness, FlashMode, State
from .vt_base import VTBase


class DNDBase(ColorableMixin, VTBase):
    """Base VT DND implementation.

    VT DND devices accept one command per HID report. After a brightness
    change the current color is resent following a short settling delay,
    matching the command sequence supplied by the manufacturer. The delay
    runs as a task in asyncio contexts so the event loop is not blocked.
    """

    BRIGHTNESS_SETTLE_DELAY = 0.1

    brightness: Brightness = Brightness.Medium

    @cached_property
    def state(self) -> State:
        """The device state manager."""
        return State()

    def __bytes__(self) -> bytes:
        return bytes(self.state)

    @cached_property
    def write_strategy(self) -> Callable[[bytes], int]:
        """Write the VT HID report without the generic Windows prefix.

        VT devices use a non-zero HID report number, which must be the
        first byte written on every platform. Light.update() prepends a
        zero byte on Windows, so it is removed here.
        """
        handle = self.hardware.handle

        def write(payload: bytes) -> int:
            if self.platform == "Windows" and payload.startswith(b"\x00"):
                payload = payload[1:]
            return handle.write(payload)

        return write

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on the DND light with the specified color.

        :param color: RGB color tuple (red, green, blue) with values 0-255
        :param led: LED index (unused for DND devices)
        """
        self.color = color
        with self.batch_update():
            self.state.set_color(self.color)

    def off(self, led: int = 0) -> None:
        """Turn off the DND light and cancel running tasks.

        Overrides the base off() to send the device's dedicated off command.

        :param led: LED index (unused for DND devices)
        """
        self.cancel_tasks()
        self.color = (0, 0, 0)
        with self.batch_update():
            self.state.off()

    def dim(self) -> None:
        """Decrease brightness one level, stopping at the lowest level."""
        if self.brightness > Brightness.Low:
            self._change_brightness(Brightness(self.brightness - 1))

    def bright(self) -> None:
        """Increase brightness one level, stopping at the highest level."""
        if self.brightness < Brightness.High:
            self._change_brightness(Brightness(self.brightness + 1))

    def flash(self, mode: FlashMode = FlashMode.ONE) -> None:
        """Start one of the firmware's predefined flash patterns.

        :param mode: Flash pattern to run
        :raises ValueError: If mode is not a FlashMode value
        """
        mode = FlashMode(mode)
        with self.batch_update():
            self.state.flash(mode)

    def _change_brightness(self, level: Brightness) -> None:
        """Send a brightness command and then resend the current color.

        :param level: Brightness level to apply
        """
        self.brightness = level
        with self.batch_update():
            self.state.set_brightness(level)

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            sleep(self.BRIGHTNESS_SETTLE_DELAY)
            self.on(self.color, interrupt=False)
        else:
            self.add_task("restore_color", self._restore_color, replace=True)

    @staticmethod
    async def _restore_color(light: "DNDBase") -> None:
        """Resend the light's color after the brightness settling delay.

        :param light: The light whose color is resent
        """
        await asyncio.sleep(light.BRIGHTNESS_SETTLE_DELAY)
        light.on(light.color, interrupt=False)

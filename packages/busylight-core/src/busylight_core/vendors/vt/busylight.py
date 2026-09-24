"""VT Busylight support."""

from collections.abc import Callable
from functools import cached_property
from time import sleep
from typing import ClassVar, Literal

from .implementation import State
from .vt_base import VTBase


class VTDND(VTBase):
    """Control VT DND Alpha and Omega devices."""

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x340B, 0xF001): "VT DND Omega",
        (0x340B, 0xF002): "VT DND Alpha",
    }

    def set_command(
        self,
        report: int,
        action: int,
        color: tuple[int, int, int],
    ) -> None:
        """Build and send a VT HID command.

        :param report: HID report identifier
        :param action: VT protocol action
        :param color: Three command data bytes
        """
        with self.batch_update():
            self.state.clear()
            self.state.report = report
            self.state.action = action
            self.color = color

    @cached_property
    def state(self) -> State:
        """Device state manager for controlling light behavior.

        Returns a State instance that manages RGB color values and
        other device-specific properties. Use this to modify device
        state before calling update() to apply changes.

        :return: State instance for managing device properties
        """
        return State()

    def __bytes__(self) -> bytes:
        return bytes(self.state)

    @property
    def color(self) -> tuple[int, int, int]:
        """Return the RGB values in the current command state."""
        return self.state.color

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        self.state.color = value

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        self.set_command(0x1, 0x4, color)

    def off(self, led: int = 0) -> None:
        """Turn off the device.

        :param led: Ignored because VT DND devices have one light target
        """
        self.set_command(0x1, 0x1, (0, 0, 0))

    def dim(self) -> None:
        """Decrease brightness by one level, stopping at one."""
        if self.state.brightness == 1:
            return
        color_snapshot = self.color
        self.state.brightness -= 1
        self.set_command(0x1, 0x9, (self.state.brightness, 0, 0))
        sleep(0.1)
        self._on(color_snapshot)

    def bright(self) -> None:
        """Increase brightness by one level, stopping at three."""
        if self.state.brightness == 3:
            return
        color_snapshot = self.color
        self.state.brightness += 1
        self.set_command(0x1, 0x9, (self.state.brightness, 0, 0))
        sleep(0.1)
        self._on(color_snapshot)

    def flash(
        self,
        color: Literal[1, 2],
    ) -> None:
        """Flash one of the device's two predefined colors.

        :param color: Device color identifier, either one or two
        :raises ValueError: If color is not one or two
        """
        if color not in (1, 2):
            message = "flash color must be 1 or 2"
            raise ValueError(message)

        self.set_command(0x1, 0x2, (color, 0, 0))

    @property
    def write_strategy(self) -> Callable[[bytes], int]:
        """Write the VT HID report without the generic Windows prefix."""
        handle = self.hardware.handle

        def write(payload: bytes) -> int:
            if self.platform == "Windows" and payload.startswith(b"\x00"):
                payload = payload[1:]

            return handle.write(payload)

        return write

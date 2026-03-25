"""Kuando Busylight Base Implementation"""

from functools import cached_property

from busylight_core.mixins import ColorableMixin

from .implementation import State
from .kuando_base import KuandoBase


class BusylightBase(ColorableMixin, KuandoBase):
    """Base Busylight implementation.

    Kuando devices require periodic keepalive packets to prevent the hardware
    from quiescing. This implementation automatically manages keepalive using
    the appropriate strategy (asyncio or threading) based on the calling context.
    """

    # EJO there are two different intervals in play with the Kuando busylight:
    #     1. refresh interval, how often the keepalive function is called
    #     2. keepalive interval, how long to wait for a keepalive before ending
    #        the current operation.
    #
    #     If the keepalive is shorter than refresh, the light will perform an
    #     uncommand flash.
    REFRESH_INTERVAL = 10
    KEEPALIVE_INTERVAL = 15

    @cached_property
    def state(self) -> State:
        """The device state manager."""
        return State()

    def __bytes__(self) -> bytes:
        return bytes(self.state)

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn on the Busylight with the specified color.

        Automatically starts keepalive using the best available strategy
        (asyncio or threading) based on the calling environment.

        :param color: RGB color tuple (red, green, blue) with values 0-255
        :param led: LED index (unused for Busylight devices)
        """
        self.color = color
        with self.batch_update():
            self.state.steps[0].jump(self.color)

        self.add_task("keepalive", self.keepalive, interval=self.REFRESH_INTERVAL)

    def off(self, led: int = 0) -> None:
        """Turn off the Busylight and cancel keepalive.

        Overrides the base off() to avoid restarting keepalive via _on().

        :param led: LED index (unused for Busylight devices)
        """
        self.cancel_tasks()
        self.color = (0, 0, 0)
        with self.batch_update():
            self.state.steps[0].jump(self.color)

    def keepalive(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Send a keepalive command to the Busylight."""
        with self.batch_update():
            self.state.steps[0].keep_alive(self.KEEPALIVE_INTERVAL)

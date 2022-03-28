""" a Manager for working with multiple USBLights
"""

import asyncio

from collections import deque
from contextlib import contextmanager
from typing import Dict, List, Optional, Union, Tuple
from loguru import logger

from .lights import LightUnavailable, USBLight
from .lights import ColorTuple, FrameGenerator, Speed


class LightManager:
    def __init__(self, greedy: bool = True, lightclass: type = None):
        """
        :greedy: bool
        :lightclass: USBLight or subclass
        """

        self.greedy = greedy

        if lightclass is None:
            self._lightclass = USBLight
        else:
            if not issubclass(lightclass, USBLight):
                raise TypeError("Not a USBLight subclass")
            self._lightclass = lightclass

    def __repr__(self) -> str:
        return "".join(
            [
                f"{self.__class__.__name__}(",
                f"greedy={self.greedy}, ",
                f"lightclass={self.lightclass!r})",
            ]
        )

    def __str__(self) -> str:
        return "\n".join(
            [f"{n:3d} {light.name}" for n, light in enumerate(self.lights)]
        )

    def __len__(self) -> int:
        return len(self.lights)

    def __del__(self) -> None:
        logger.debug(f"releasing resources for LightManager {id(self)}")
        self.release()

    @property
    def lightclass(self) -> USBLight:
        return getattr(self, "_lightclass", USBLight)

    @property
    def lights(self) -> List[USBLight]:
        """List of managed lights."""
        try:
            return self._lights
        except AttributeError:
            pass
        self._lights = list(self.lightclass.all_lights(reset=False))
        logger.debug(f"found {len(self._lights)}")
        return self._lights

    def selected_lights(self, indices: List[int] = None) -> List[USBLight]:
        """Return a list of USBLights matching the list of `indices`.

        If `indices` is empty, all managed lights are returned.

        If there are no lights with matching indices, an empty list is returned.

        :indices: List[int]
        :return: List[USBLight]
        """
        if not indices:
            indices = range(0, len(self.lights))

        selected_lights = []
        for index in indices:
            try:
                selected_lights.append(self.lights[index])
                logger.debug(f"{index=} {self.lights[index]!s}")
            except IndexError as error:
                logger.debug(f"{index=} {error}")

        return selected_lights

    def update(self) -> Tuple[int, int, int]:
        """Updates managed lights list.

        1. Looks for lights that have plugged in since last update
        2. Checks current lights if they are still plugged in
        3.
        3. Combines new and remaining lights

        :return: Tuple[# of new lights, # of old lights, # of unavailable lights]

        """
        new_lights = self.lightclass.all_lights()
        logger.debug(f"{len(new_lights)} {new_lights=}")

        old_lights = [light for light in self.lights if light.is_pluggedin]
        logger.debug(f"{len(old_lights)} {old_lights=}")

        ded_lights = [light for light in self.lights if light.is_unplugged]
        logger.debug(f"{len(ded_lights)} {ded_lights=}")

        self._lights = sorted(old_lights + new_lights)
        logger.debug(f"{len(self.lights)} {self.lights=}")

        return len(new_lights), len(old_lights), len(ded_lights)

    def release(self) -> None:
        """Release managed lights."""
        try:
            logger.debug(f"starting to release {len(self._lights)} lights")
            while light := self._lights.pop():
                del light

        except (IndexError, AttributeError) as error:
            logger.debug(f"during release {error}")

        try:
            del self._lights
        except AttributeError as error:
            logger.debug(f"during release, failed to del _lights {error}")

        logger.debug("completed releasing lights")

    @contextmanager
    def operate_on(
        self,
        lights: List[int] = None,
        off_on_enter: bool = True,
        off_on_exit: bool = True,
    ):

        if off_on_enter:
            self.off(lights=lights)

        yield self

        if off_on_exit:
            self.off(lights=lights)

    async def on_supervisor(
        self,
        color: ColorTuple,
        lights: List[USBLight],
        timeout: float = None,
    ) -> None:
        """Turns on all the lights with the given color, asynchronously.

        Each light's `on` method is called with the supplied `color` which
        may optionally return an `Awaitable` coroutine which the light
        requires to remain on. After collecting all these coroutines, the
        supervisor awaits the exit of those coroutines. If a timeout in
        seconds is specified, the coroutines will be stopped at the end
        of the period.

        :color: ColorTuple
        :lights: List[USBLight]
        :timeout: float seconds
        """
        logger.debug(f"{color=} {lights=} {timeout=}")

        awaitables = []
        for light in lights:
            if awaitable := light.on(color):
                awaitables.append(awaitable())

        if awaitables:
            done, pending = await asyncio.wait(awaitables, timeout=timeout)

    async def effect_supervisor(
        self,
        effect: FrameGenerator,
        lights: List[USBLight],
        timeout: float = None,
    ) -> None:
        """Builds a list of awaitable coroutines to perform the given `effect`
        on each of the `lights` and awaits the exit of the coroutines (which
        typically do not exit). If a timeout in seconds is specified, the
        effect will stop at the end of the period.

        :effect: FrameGenerator
        :lights: List[USBLight]
        :timeout: float seconds
        """

        if not lights:
            logger.debug("no lights were passed to effect_supervisor")
            return

        done, pending = await asyncio.wait(
            (light.apply_effect(effect) for light in lights),
            timeout=timeout,
        )

    def off(self, lights: List[int] = None) -> None:
        """Turn off all the lights whose indices are in the `lights` list.

        :lights: List[int]
        """
        logger.debug(f"{lights=}")

        for light in self.selected_lights(lights):
            light.off()

    def on(
        self,
        color: ColorTuple,
        lights: List[int] = None,
        timeout: float = None,
    ) -> None:
        """Turn on all the lights whose indices are in the `lights` list.

        :color: ColorTuple
        :lights: List[int]
        :timeout: float seconds
        """

        try:
            logger.debug(f"begin on_supervisor event loop {timeout=}")
            asyncio.run(
                self.on_supervisor(color, self.selected_lights(lights), timeout)
            )
            logger.debug("  end on_supervisor event loop")
            self.off(lights)
        except KeyboardInterrupt:
            self.off(lights)

    def apply_effect(
        self,
        effect: FrameGenerator,
        lights: List[int],
        timeout: float = None,
    ) -> None:
        """Applies the given `effect` to all of the lights whose indices are
        in the `lights` list.

        :effect: FrameGenerator
        :lights: List[int]
        :timeout: float seconds
        """

        try:
            logger.debug(f"begin effect_supervisor event loop {timeout=}")
            asyncio.run(
                self.effect_supervisor(effect, self.selected_lights(lights), timeout)
            )
            logger.debug("  end effect_supervisor event loop")
            self.off(lights)
        except KeyboardInterrupt:
            self.off(lights)

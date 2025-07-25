"""a Manager for controlling multiple Lights."""

import asyncio
from contextlib import suppress
from functools import cached_property
from typing import Optional

from busylight_core import Light, LightUnavailableError, NoLightsFoundError
from loguru import logger

from .effects import Effects


class LightManager:
    @staticmethod
    def parse_target_lights(targets: Optional[str]) -> list[int]:
        """Parses the `targets` string to produce a list of indicies.

        The targets string may be:
        - None, meaning choose first light
        - empty, meaning all lights
        - a single integer, specifying one line
        - [0-9]+[-:][0-9]+[,]* specifying a range.

        :return: list[int]
        """
        if targets is None:
            return [0]

        lights = []
        for target in targets.split(","):
            for sep in ["-", ":"]:
                if sep in target:
                    start, _, end = target.partition(sep)
                    lights.extend(list(range(int(start), int(end) + 1)))
                    break
                with suppress(ValueError):
                    lights.append(int(target))
        return list(set(lights))

    def __init__(self, lightclass: type = None):
        """Initializes the LightManager.

        :param lightclass: Light or subclass

        If the caller supplies a `lightclass`, which is expected to
        be Light or a subclass, the light manager will only
        manage lights returned by `lightclass.all_lights()`. If the
        user does not supply a class, the default is `Light`.
        """

        self.lightclass = lightclass or Light

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lightclass={self.lightclass!r}"

    def __str__(self) -> str:
        return "\n".join(
            [f"{n:3d} {light.name}" for n, light in enumerate(self.lights)],
        )

    def __len__(self) -> int:
        return len(self.lights)

    def __del__(self) -> None:
        logger.info(f"releasing resources for LightManager {id(self)}")
        self.release()

    @property
    def lightclass(self) -> Light:
        """Light subclass used to locate lights, read-only."""
        return getattr(self, "_lightclass", Light)

    @lightclass.setter
    def lightclass(self, value: type[Light]) -> None:
        if not isinstance(value, type):
            msg = f"lightclass must be a Light subclass, not {value!r}"
            raise ValueError(msg)
        self._lightclass = value

    @property
    def lights(self) -> list[Light]:
        """List of managed lights."""
        try:
            return self._lights
        except AttributeError:
            self._lights = sorted(self.lightclass.all_lights(reset=False))
            return self._lights

    def selected_lights(self, indices: list[int] = None) -> list[Light]:
        """Return a list of Lights matching the list of `indices`.

        If `indices` is empty, all managed lights are returned.

        If there are no lights with matching indices, an empty list is returned.

        :param indices: list[int]

        Raises:
        - NoLightsFoundError

        """

        if not indices:
            return self.lights

        selected_lights = []
        for index in indices:
            try:
                selected_lights.append(self.lights[index])
            except IndexError as error:
                logger.info(f"index:{index} {error}")

        if selected_lights:
            return selected_lights

        raise NoLightsFoundError(indices)

    def update(self, greedy: bool = True) -> tuple[int, int, int]:
        """Updates managed lights list.

        This method looks for newly plugged in lights if the greedy
        argument is True. It then surveys known lights, building a
        count of plugged in lights and unplugged lights. New lights
        are appended to the end of the `lights` property in order to
        keep the light index order stable over the lifetime of the
        manager. The return value is an integer three-tuple which
        records the number of new lights found, the number of
        previously known lights that are still active and the number
        of previously known lights that are now inactive.

        :return: Tuple[# new lights, # active lights, # inactive lights]
        """
        if greedy:
            new_lights = self.lightclass.all_lights()
            logger.debug(f"{len(new_lights)} new {new_lights}")

        active_lights = [light for light in self.lights if light.is_pluggedin]

        inactive_lights = [light for light in self.lights if light.is_unplugged]

        self._lights += new_lights

        return len(new_lights), len(active_lights), len(inactive_lights)

    def release(self) -> None:
        """Release managed lights."""
        # EJO Is this better than calling self._lights.clear()?
        #     This implementation forces the finalization of each
        #     light and adds some logging. I'm not sure it's
        #     worth the added complexity.
        try:
            while self._lights:
                light = self._lights.pop()
                light.reset()
                light.release()
                del light
        except (IndexError, AttributeError) as error:
            logger.error(f"during release {error}")

        try:
            del self._lights
        except AttributeError as error:
            logger.error(f"during release, failed to del _lights property {error}")

    def on(
        self,
        color: tuple[int, int, int],
        light_ids: list[int] = None,
        timeout: float = None,
    ) -> None:
        """Turn on all the lights whose indices are in the `lights` list.

        :color: tuple[int,int,int]
        :lights: list[int]
        :timeout: float seconds

        Raises:
        - NoLightsFoundError

        """
        asyncio.run(self.on_supervisor(color, self.selected_lights(light_ids), timeout))

    async def on_supervisor(
        self,
        color: tuple[int, int, int],
        lights: list[Light],
        timeout: float = None,
        wait: bool = True,
    ) -> None:
        """Async monitor for activating specified lights with the given color.

        :param color: tuple[int, int, int]
        :param lights: list[Light]
        :param timeout: float
        :param wait: bool

        Raises:
        - TimeoutError

        """
        awaitables = []
        for light in lights:
            light.on(color)
            awaitables.extend(light.tasks.values())

        if awaitables and wait:
            done, pending = await asyncio.wait(awaitables, timeout=timeout)
            if pending:
                raise TimeoutError(f"On operation timed out {timeout}")

    def apply_effect(
        self,
        effect: Effects,
        light_ids: list[int] = None,
        timeout: float = None,
    ) -> None:
        """Applies the given `effect` to all of the lights whose indices are
        in the `lights` list.

        :effect: FrameGenerator
        :lights: list[int]
        :timeout: float seconds

        Raises:
        - NoLightsFoundError

        """
        asyncio.run(
            self.effect_supervisor(effect, self.selected_lights(light_ids), timeout),
        )

    async def effect_supervisor(
        self,
        effect: Effects,
        lights: list[Light],
        timeout: float = None,
        wait: bool = True,
    ) -> None:
        """Builds a list of awaitable coroutines to perform the given `effect`
        on each of the `lights` and awaits the exit of the coroutines (which
        typically do not exit). If a timeout in seconds is specified, the
        effect will stop at the end of the period.

        :effect:
        :lights: List[Light]
        :timeout: float seconds

        Raises:
        - TimoutError if a timeout is specified and effects are still running.

        """
        awaitables = []
        for light in lights:
            light.cancel_tasks()
            light.add_task(effect.name, effect)
            awaitables.extend(light.tasks.values())

        if awaitables and wait:
            done, pending = await asyncio.wait(awaitables, timeout=timeout)
            if pending:
                raise TimeoutError(f"Effect {effect} timed out {timeout}")

    def off(self, lights: list[int] = None) -> None:
        """Turn off all the lights whose indices are in the `lights` list.

        :lights: List[int]

        Raises:
        - NoLightsFoundError

        *Note*: This method is not asynchronnous as all known lights
                deactive without excessive software mediation and drama.

        """
        for light in self.selected_lights(lights):
            try:
                light.off()
            except LightUnavailableError as error:
                logger.debug("{light} is {error}")

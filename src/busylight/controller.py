"""Aggregate Light controller with fluent interface.

This module provides a controller architecture for managing USB LED lights
through the busylight-core library using fluent interfaces and light selections.

The main components are:
- :class:`LightSelection`: A collection of lights that can have operations applied
- :class:`LightController`: Main controller with fluent interface for light discovery and selection

Example:
    Basic usage of the light controller::

        from busylight.controller import LightController

        # Create controller and turn on all lights
        with LightController() as controller:
            controller.all().turn_on((255, 0, 0))  # Red

        # Apply effects to specific lights
        controller.by_name("Kuando").blink((0, 255, 0), count=5)
"""

from __future__ import annotations

import asyncio
import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator, Pattern

from busylight_core import Light, LightUnavailableError, NoLightsFoundError
from loguru import logger

from .effects import Effects
from .speed import Speed


@dataclass
class LightSelection:
    """A selection of lights that can have operations applied to them.

    This class represents a collection of lights that can be manipulated as a group.
    It provides methods for turning lights on/off, applying effects like blinking,
    and managing light states. Operations are applied to all lights in the selection.

    :param lights: List of Light objects managed by this selection
    :type lights: list[Light]

    Example:
        Create and use a light selection::

            lights = [light1, light2, light3]
            selection = LightSelection(lights)
            selection.turn_on((255, 0, 0))  # Turn all lights red
            selection.blink((0, 255, 0), count=3)  # Blink green 3 times
    """

    lights: list[Light] = field(default_factory=list)

    def __len__(self) -> int:
        """Return the number of lights in this selection."""
        return len(self.lights)

    def __bool__(self) -> bool:
        """Return True if the selection contains any lights."""
        return bool(self.lights)

    def __iter__(self) -> Iterator[Light]:
        """Return an iterator over the lights in this selection."""
        return iter(self.lights)

    def turn_on(self, color: tuple[int, int, int], led: int = 0) -> LightSelection:
        """Turn on all lights in the selection with the specified color.

        :param color: RGB color tuple with values 0-255
        :param led: Target LED index. 0 affects all LEDs, 1+ targets specific LEDs

        For devices with multiple LEDs (like Blink1 mk2), use led parameter to control
        individual LEDs. Single-LED devices ignore this parameter. LED indexing is
        device-specific but typically: 0=all, 1=first/top, 2=second/bottom, etc.

        Example:
            Turn all LEDs red::

                selection.turn_on((255, 0, 0))  # led=0 default

            Turn only top LED of Blink1 mk2 blue::

                selection.turn_on((0, 0, 255), led=1)
        """

        for light in self.lights:
            try:
                light.on(color, led=led)
            except LightUnavailableError as error:
                logger.debug(f"Light unavailable during turn_on: {error}")

        return self

    def turn_off(self) -> LightSelection:
        """Turn off all lights in the selection.

        Cancels any running tasks on lights that support task management
        before turning them off. Handles errors gracefully by logging them
        and continuing with other lights.
        """
        for light in self.lights:
            try:
                if hasattr(light, "cancel_tasks"):
                    light.cancel_tasks()
                light.off()
            except LightUnavailableError as error:
                logger.debug(f"Light unavailable during turn_off: {error}")
            except Exception as error:
                logger.debug(f"Error during turn_off: {error}")
                try:
                    light.off()
                except Exception as off_error:
                    logger.debug(f"Error during light.off(): {off_error}")
        return self

    def blink(
        self,
        color: tuple[int, int, int],
        count: int = 0,
        speed: str = "slow",
        led: int = 0,
    ) -> LightSelection:
        """Apply blink effect to all lights in the selection.

        :param color: RGB color tuple with values 0-255
        :param count: Number of blinks. 0 means infinite blinking
        :param speed: Blink speed - "slow", "medium", or "fast"
        :param led: Target LED index. 0 affects all LEDs, 1+ targets specific LEDs

        For devices with multiple LEDs, use led parameter to blink specific LEDs.
        Single-LED devices ignore this parameter.

        Example:
            Blink all LEDs green 5 times at fast speed::

                selection.blink((0, 255, 0), count=5, speed="fast")

            Blink only bottom LED of Blink1 mk2::

                selection.blink((255, 0, 0), led=2)
        """
        try:
            speed_obj = Speed(speed)
        except ValueError:
            speed_obj = Speed.slow

        effect = Effects.for_name("blink")(color, count=count)
        return self.apply_effect(effect, interval=speed_obj.duty_cycle, led=led)

    def apply_effect(
        self,
        effect: Effects,
        duration: float | None = None,
        interval: float | None = None,
        led: int = 0,
    ) -> LightSelection:
        """Apply a custom effect to all lights in the selection.

        :param effect: The effect to apply to the lights
        :param duration: Maximum duration in seconds. None for no limit
        :param interval: Interval between effect updates. None uses effect default
        :param led: LED index to target (0 = all LEDs, 1+ = specific LED)

        The effect runs asynchronously using asyncio. If no event loop is running,
        one will be created. The method handles keyboard interrupts gracefully.
        """
        actual_interval = interval if interval is not None else effect.default_interval

        async def effect_supervisor():
            tasks = []
            for light in self.lights:
                light.cancel_tasks()

                async def effect_task(target_light=light):
                    return await effect.execute(target_light, actual_interval, led)

                task = light.add_task(
                    name=effect.name.lower(),
                    func=effect_task,
                    priority=effect.priority,
                    replace=True,
                )
                tasks.append(task)

            if tasks:
                if duration:
                    done, pending = await asyncio.wait(tasks, timeout=duration)
                    for task in pending:
                        task.cancel()
                elif hasattr(effect, "count") and effect.count > 0:
                    await asyncio.wait(tasks)
                else:
                    try:
                        await asyncio.wait(tasks)
                    except KeyboardInterrupt:
                        for task in tasks:
                            task.cancel()
                        raise

        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(effect_supervisor())
        except RuntimeError:
            try:
                asyncio.run(effect_supervisor())
            except KeyboardInterrupt:
                pass

        return self



class LightController:
    """Light controller with fluent interface for managing USB LED lights.

    This controller provides a high-level interface for discovering, selecting,
    and controlling USB LED lights. It uses the busylight-core library for
    device communication and provides fluent methods for light selection.

    :param light_class: Optional Light class to use for device discovery.
                       Defaults to busylight_core.Light

    Example:
        Basic controller usage::

            controller = LightController()

            # Turn on all lights
            controller.all().turn_on((255, 0, 0))

            # Select specific lights
            controller.by_name("Kuando").blink((0, 255, 0))
            controller.by_index(0, 2).turn_off()

            # Use as context manager for automatic cleanup
            with LightController() as ctrl:
                ctrl.first().turn_on((0, 0, 255))
    """

    def __init__(self, light_class: type = None) -> None:
        """Initialize the light controller.

        :param light_class: Light class to use for device discovery
        """
        self.light_class = light_class or Light
        self._lights: set[Light] = set()

    @property
    def lights(self) -> list[Light]:
        """All managed lights, sorted by name.

        Discovers available lights using the configured light class and
        caches them for future use. Returns lights sorted alphabetically
        by their name property.
        """
        try:
            if found := self.light_class.all_lights(exclusive=True, reset=False):
                self._lights.update(found)
        except Exception as error:
            logger.warning(f"Failed to get lights: {error}")
        return sorted(self._lights)

    def __enter__(self) -> LightController:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and cleanup resources."""
        self.cleanup()

    async def __aenter__(self) -> LightController:
        """Enter async context manager."""
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and cleanup resources."""
        return self.__exit__(exc_type, exc_val, exc_tb)

    def cleanup(self) -> None:
        """Turn off all lights and clean up resources.

        Cancels any running tasks and turns off all managed lights.
        Errors are logged but do not prevent cleanup of other lights.
        """
        for light in self.lights:
            try:
                if hasattr(light, "cancel_tasks"):
                    light.cancel_tasks()
                light.off()
            except Exception as error:
                logger.error(f"Error turning off light during cleanup: {error}")

    def release_lights(self) -> None:
        """Release all owned lights and clear the cache.

        Calls the release method on all cached lights to free hardware
        resources, then clears the internal light cache. Errors during
        release are logged but do not prevent releasing other lights.
        """
        for light in self._lights:
            try:
                light.release()
            except Exception as error:
                logger.warning(f"Failed to release light {light.name}: {error}")
        self._lights = set()

    def has_active_tasks(self) -> bool:
        """Check if any lights have active tasks running.

        Useful for determining if the application should keep running
        to allow light effects to complete, particularly for lights
        like Kuando that require keepalive tasks.
        """
        return any(bool(light.tasks) for light in self.lights)

    def wait_for_tasks(self) -> None:
        """Wait indefinitely for all light tasks to complete or until interrupted.

        This method blocks until all light tasks complete naturally or are
        interrupted by the user. It's particularly useful for CLI applications
        that need to keep running while light effects are active.

        The method handles both sync and async contexts, creating an event
        loop if needed. Keyboard interrupts are handled gracefully by
        canceling all tasks before exiting.
        """
        if not self.has_active_tasks():
            return

        async def task_supervisor():
            """Monitor all light tasks and wait for them."""
            while True:
                all_tasks = []
                for light in self.lights:
                    all_tasks.extend(light.tasks.values())

                if not all_tasks:
                    break

                try:
                    await asyncio.wait(all_tasks, return_when=asyncio.FIRST_COMPLETED)
                except KeyboardInterrupt:
                    for light in self.lights:
                        light.cancel_tasks()
                    raise

        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(task_supervisor())
        except RuntimeError:
            try:
                asyncio.run(task_supervisor())
            except KeyboardInterrupt:
                pass

    def all(self) -> LightSelection:
        """Select all discovered lights.

        Example:
            Turn on all lights::

                controller.all().turn_on((255, 255, 255))
        """
        return LightSelection(self.lights)

    def first(self) -> LightSelection:
        """Select the first discovered light.

        Lights are sorted alphabetically by name, so this returns
        the light with the lexicographically smallest name.

        Example:
            Turn on the first light::

                controller.first().turn_on((0, 255, 0))
        """
        lights = self.lights
        return LightSelection(lights[:1] if lights else [])

    def by_index(self, *indices: int) -> LightSelection:
        """Select lights by their zero-based index positions.

        :param indices: One or more zero-based indices of lights to select

        Invalid indices are logged as warnings and ignored. The lights
        list is sorted alphabetically by name before indexing.

        Example:
            Select the first and third lights::

                controller.by_index(0, 2).blink((255, 0, 0))
        """
        lights = self.lights
        selected = []
        for index in indices:
            try:
                selected.append(lights[index])
            except IndexError:
                logger.warning(f"Light index {index} not found")
        return LightSelection(selected)

    def by_name(self, name: str, index: int = None) -> LightSelection:
        """Select lights by their device name.

        :param name: Exact name of the light device to match
        :param index: Optional index when multiple lights have the same name

        If multiple lights have the same name and no index is specified,
        all matching lights are selected. Use the index parameter to select
        a specific light when there are duplicates.

        Example:
            Select all Kuando lights::

                controller.by_name("Kuando Busylight").turn_on((0, 0, 255))

            Select the second Kuando light specifically::

                controller.by_name("Kuando Busylight", index=1).blink((255, 0, 0))
        """

        matching = [light for light in self.lights if light.name == name]

        if not matching:
            logger.warning(f"No lights found with name '{name}'")
            return LightSelection([])

        if index is None:
            return LightSelection(matching)

        try:
            return LightSelection([matching[index]])
        except IndexError:
            logger.warning(f"Light '{name}' index {index} not found")
            return LightSelection([])

    def by_pattern(self, pattern: str | Pattern) -> LightSelection:
        """Select lights whose names match a regular expression pattern.

        :param pattern: Regular expression pattern string or compiled Pattern object

        String patterns are compiled with case-insensitive matching.
        The pattern is searched within the light name, not matched exactly.

        Example:
            Select all lights containing "USB"::

                controller.by_pattern("USB").turn_off()

            Select lights starting with "Luxafor"::

                controller.by_pattern(r"^Luxafor").blink((255, 255, 0))
        """
        if isinstance(pattern, str):
            pattern = re.compile(pattern, re.IGNORECASE)

        matching = [light for light in self.lights if pattern.search(light.name)]
        return LightSelection(matching)

    def names(self) -> list[str]:
        """Get display names for all lights with duplicates numbered.

        When multiple lights have the same name, they are numbered
        sequentially (e.g., "Kuando Busylight #1", "Kuando Busylight #2").
        Unique names are returned without numbering.

        Example:
            Print all light names::

                for name in controller.names():
                    print(f"Found light: {name}")
        """
        lights = self.lights
        name_counts = {}
        display_names = []

        for light in lights:
            name_counts[light.name] = name_counts.get(light.name, 0) + 1

        name_indices = {}
        for light in lights:
            name = light.name
            if name_counts[name] > 1:
                name_indices[name] = name_indices.get(name, 0) + 1
                display_names.append(f"{name} #{name_indices[name]}")
            else:
                display_names.append(name)

        return display_names

    def __len__(self) -> int:
        """Return the number of discovered lights."""
        return len(self.lights)

    def __bool__(self) -> bool:
        """Return True if any lights have been discovered."""
        return bool(self.lights)

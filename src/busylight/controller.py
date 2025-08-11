"""Aggregate Light controller with fluent interface."""

from __future__ import annotations

import asyncio
import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Pattern

from busylight_core import Light, LightUnavailableError, NoLightsFoundError
from loguru import logger

from .effects import Effects
from .speed import Speed


@dataclass
class LightSelection:
    """A selection of lights that can have operations applied to them."""

    lights: list[Light] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lights)

    def __bool__(self) -> bool:
        return bool(self.lights)

    def __iter__(self):
        return iter(self.lights)

    def turn_on(self, color: tuple[int, int, int]) -> LightSelection:
        """Turn on selected lights."""

        for light in self.lights:
            try:
                light.on(color)
            except LightUnavailableError as error:
                logger.debug(f"Light unavailable during turn_on: {error}")

        return self

    def turn_off(self) -> LightSelection:
        """Turn off selected lights."""
        for light in self.lights:
            try:
                # Cancel any running tasks (like blink) before turning off
                light.cancel_tasks()
                light.off()
            except LightUnavailableError as error:
                logger.debug(f"Light unavailable during turn_off: {error}")
            except AttributeError:
                # Light doesn't support task cancellation, just turn off
                light.off()
        return self

    def blink(
        self,
        color: tuple[int, int, int],
        count: int = 0,
        speed: str = "slow",
    ) -> LightSelection:
        """Apply blink effect to selected lights."""
        try:
            speed_obj = Speed(speed)
        except ValueError:
            speed_obj = Speed.slow

        effect = Effects.for_name("blink")(color, count=count)
        return self.apply_effect(effect, interval=speed_obj.duty_cycle)

    def apply_effect(
        self,
        effect: Effects,
        duration: float | None = None,
        interval: float | None = None,
    ) -> LightSelection:
        """Apply a custom effect to selected lights."""
        actual_interval = interval if interval is not None else effect.default_interval

        for light in self.lights:
            light.cancel_tasks()

            async def effect_task(target_light=light):
                return await effect.execute(target_light, actual_interval)

            task = light.add_task(
                name=effect.name.lower(),
                func=effect_task,
                priority=effect.priority,
                replace=True,
            )

            if duration:
                asyncio.create_task(asyncio.wait_for(task, timeout=duration))

        return self


class LightController:
    """Light controller with fluent interface."""

    def __init__(self, light_class: type = None) -> None:
        self.light_class = light_class or Light
        self._lights: set[Light] = set()

    @property
    def lights(self) -> list[Light]:
        """All managed lights, sorted by name."""
        try:
            if found := self.light_class.all_lights(exclusive=True, reset=False):
                self._lights.update(found)
        except Exception as error:
            logger.warning(f"Failed to get lights: {error}")
        return sorted(self._lights)

    def __enter__(self) -> LightController:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)

    def cleanup(self) -> None:
        """Turn off all lights and clean up."""
        for light in self.lights:
            try:
                light.off()
            except Exception as error:
                logger.error(f"Error turning off light during cleanup: {error}")

    def release_lights(self) -> None:
        """Release all owned lights."""
        for light in self._lights:
            try:
                light.release()
            except Exception as error:
                logger.warning(f"Failed to release light {light.name}: {error}")
        self._lights = set()

    # Fluent selection methods
    def all(self) -> LightSelection:
        """Select all lights."""
        return LightSelection(self.lights)

    def first(self) -> LightSelection:
        """Select the first light."""
        lights = self.lights
        return LightSelection(lights[:1] if lights else [])

    def by_index(self, *indices: int) -> LightSelection:
        """Select lights by index."""
        lights = self.lights
        selected = []
        for index in indices:
            try:
                selected.append(lights[index])
            except IndexError:
                logger.warning(f"Light index {index} not found")
        return LightSelection(selected)

    def by_name(self, name: str, index: int = None) -> LightSelection:
        """Select lights by name, optionally by index for duplicates."""

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
        """Select lights matching a regex pattern."""
        if isinstance(pattern, str):
            pattern = re.compile(pattern, re.IGNORECASE)

        matching = [light for light in self.lights if pattern.search(light.name)]
        return LightSelection(matching)

    def names(self) -> list[str]:
        """Get light names with duplicates numbered."""
        lights = self.lights
        name_counts = {}
        display_names = []

        # Count occurrences
        for light in lights:
            name_counts[light.name] = name_counts.get(light.name, 0) + 1

        # Generate display names
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
        return len(self.lights)

    def __bool__(self) -> bool:
        return bool(self.lights)

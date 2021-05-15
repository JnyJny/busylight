"""A USBLight Manager
"""

from contextlib import contextmanager, suppress
from enum import Enum
from functools import partial
from time import sleep
from typing import ContextManager, Generator, Dict, List, Tuple, Union

from .lights import USBLight
from .lights import USBLightUnknownVendor
from .lights import USBLightUnknownProduct
from .lights import USBLightInUse
from .lights import USBLightIOError

from .color import color_to_rgb

ALL_LIGHTS: int = -1


class BlinkSpeed(str, Enum):
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"

    def to_numeric_value(self) -> int:
        """Map the BlinkSpeed to a numeric value; low:1, medium:2 and fast:3.

        Returns 1 by default.

        :return: int
        """
        return {"slow": 1, "medium": 2, "fast": 3}.get(self.value, 1)


class LightIdRangeError(Exception):
    def __init__(self, light_id: int, max_id: int = 0):
        self.light_id = light_id
        self.max_id = max_id

    def __str__(self):
        return f"Light '{self.light_id}' not in the range of 0..{self.max_id}"


class ColorLookupError(Exception):
    def __init__(self, color: str):
        self.color = color

    def __str__(self):
        return f"Unable to decode color for string '{self.color}'"


class LightManager:
    """USB device manager and proxy.

    The LightManager class opens all available lights and sends commands
    to the lights without the caller having to maintain a USBLight
    object. This class also supports long-lived per-light animations via
    threading.
    """

    @classmethod
    def available(cls) -> List[USBLight]:
        """A list of currently available lights.

        The list is returned in sorted order, by filesystem path.

        :return: List[USBLight]
        """

        return sorted(USBLight.all_lights(), key=lambda v: v.path)

    def __init__(self) -> None:
        self.update()

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __str__(self) -> str:

        result = []
        for i, light in enumerate(self.lights):
            result.append(f"{i:2d}: {light.name}")

        return "\n".join(result)

    @property
    def supported(self) -> List[str]:
        """A list of supported light names."""
        try:
            return self._supported
        except AttributeError:
            pass
        self._supported: List[str] = []
        for light in USBLight.supported_lights():
            self._supported.append(f"{light.vendor} {light.__name__.replace('_',' ')}")
        return self._supported

    @property
    def lights(self) -> List[USBLight]:
        """List of manged USBLight devices

        The devices are open for use exclusively by the manager.
        """
        try:
            return self._lights
        except AttributeError:
            pass
        self._lights: List[USBLight] = []
        return self._lights

    # EJO __get_item__ implementation here to allow slice notation?
    #     maybe make LightManager an iterator?

    def lights_for(self, light_id: Union[int, None] = ALL_LIGHTS) -> List[USBLight]:
        """Returns a list of USBLights that match `light_id`, which can be
        None, -1 or a positive integer.

        If `light_id` is None, no lights are matched and an empty list is
        returned.

        A `light_id` value of -1 signals "all lights" and the entire list
        of managed lights is returned.

        A zero or positive `light_id` will return a list containing the
        matching light.

        Indices less than -1 or that trigger a IndexError raise a
        LightIdRangeError exception.

        :param light_id: Union[int, None]
        :return: List[USBLight]

        Raises:
        - LightIdRangeError
        """

        if light_id is None:
            return []

        if light_id < ALL_LIGHTS:
            raise LightIdRangeError(light_id, len(self.lights) - 1)

        try:
            return self.lights if light_id == ALL_LIGHTS else [self.lights[light_id]]
        except IndexError:
            raise LightIdRangeError(light_id, len(self.lights) - 1) from None

    def update(self):
        """Acquires new lights and purges unplugged lights.

        Light identfiers of remaining lights will change after `update`
        if lights are unplugged.

        :return: number of new lights added to the managed `lights` list.
        """

        self.lights.extend(USBLight.all_lights())
        self.lights.sort(key=lambda v: v.path)

        for dead_light in [l for l in self.lights if not l.is_acquired]:
            self.lights.remove(dead_light)

    def release(self) -> None:
        """Releases all the lights and empties the `lights` property.

        Call `update` to repopulate the `lights` property.
        """

        for light in self.lights:
            light.release()

        self.lights.clear()

    def light_on(
        self, light_id: Union[int, None] = ALL_LIGHTS, color: str = "green"
    ) -> None:
        """Turn on a light or all lights with supplied color value.

        If light_id is -1 the operation is applied to all lights.

        :param light_id: int
        :param color: 3-tuple of red, green and blue 8-bit integers

        Raises:
        - LightIdRangeError
        - ColorLookupError
        """

        try:
            rgb = color_to_rgb(color)
        except ValueError:
            raise ColorLookupError(color) from None

        for light in self.lights_for(light_id):
            light.stop_animation()
            try:
                light.on(rgb)
            except USBLightIOError as error:
                pass

    def light_off(self, light_id: Union[int, None] = ALL_LIGHTS) -> None:
        """Turn off a light or all lights.

        If light_id is -1 the operation is applied to all lights.

        :param light_id: Union[int, None]

        Raises:
        - LightIdRangeError
        """

        for light in self.lights_for(light_id):
            light.stop_animation()
            try:
                light.off()
            except USBLightIOError as error:
                pass

    def light_blink(
        self,
        light_id: Union[int, None] = ALL_LIGHTS,
        color: str = "red",
        speed: BlinkSpeed = BlinkSpeed.SLOW,
    ) -> None:
        """Start a light or lights blinking with the supplied color and speed.

        :param light_id: int
        :param color: str
        :param speed: BlinkSpeed

        - LightIdRangeError
        - ColorLookupError
        """

        try:
            rgb = color_to_rgb(color)
        except ValueError:
            raise ColorLookupError(color) from None

        self.light_off(light_id)

        for light in self.lights_for(light_id):
            try:
                light.blink(rgb, speed.to_numeric_value())
            except USBLightIOError as error:
                pass

    def apply_effect_to_light(
        self, light_id: Union[int, None], effect: Generator, *args, **kwds
    ):
        """Apply an effect function to the specified light.

        :param light_id: int
        :param effect: generator
        :param args:
        :param kwds:
        """

        self.light_off(light_id)

        try:
            color = color_to_rgb(kwds["color"])
        except KeyError:
            color = (255, 0, 0)
        except ValueError:
            raise ColorLookupError(kwds["color"])
        finally:
            effect = partial(effect, color=color)

        for light in self.lights_for(light_id):
            light.start_animation(effect)

    @contextmanager
    def operate_on(
        self,
        light_id: Union[int, None] = ALL_LIGHTS,
        wait_on_animation: bool = True,
        off_on_enter: bool = True,
        off_on_exit: bool = False,
    ) -> "LightManager":
        """This context manager method sets the lights specified by `light_id`
        to a known state, 'off', upon entering and exiting the context manager.

        If `off_on_enter` is False, the lights are not turned off on enter.
        If `off_on_exit` is False, the lights are not turned off on exit.

        :param light_id: Union[int, None]
        :param off_on_enter: bool
        :param wait_on_animation: bool
        :param off_on_exit: bool
        """

        if off_on_enter:
            self.light_off(light_id)

        yield self

        # EJO this is an ugly hack.
        if wait_on_animation:
            lights = list(self.lights_for(light_id))
            try:
                while True:
                    if any(light.is_animating for light in lights):
                        sleep(1.0)
                        continue
                    break
            except KeyboardInterrupt:
                off_on_exit = True

        if off_on_exit:
            self.light_off(light_id)

"""A USBLight Manager
"""

from contextlib import contextmanager
from enum import Enum
from typing import Callable, Dict, List, Tuple, Union

import hid

from .lights import SUPPORTED_LIGHTS, KNOWN_VENDOR_IDS
from .lights import UnknownUSBLight, USBLightInUse
from .lights import USBLight

from .color import color_to_rgb


class BlinkSpeed(str, Enum):
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"

    def to_int(self):
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
    """
    """

    def __init__(self):
        self.update()

    @property
    def supported(self) -> List[str]:
        """
        """
        try:
            return self._supported
        except AttributeError:
            pass
        self._supported = []
        for light in SUPPORTED_LIGHTS:
            self._supported.append(f"{light.__vendor__} {light.__name__}")
        return self._supported

    @property
    def available(self) -> List[Dict[str, Union[str, int]]]:
        """A list of dictionaries describing currently available lights.
        """
        lights = []
        for vendor_id in KNOWN_VENDOR_IDS:
            lights.extend(hid.enumerate(vendor_id))
        return lights

    @property
    def lights(self) -> List[USBLight]:
        """List of USBLight subclasses that the manager is currently
        controlling. 
        """
        try:
            return self._lights
        except AttributeError:
            pass
        self._lights = []
        return self._lights

    def lights_for(self, light_id: Union[int, None] = -1) -> List[USBLight]:
        """

        :param light_id: Union[int, None]
        :return: List[USBLight]
        """

        if light_id is None:
            return []

        try:
            return self.lights if light_id == -1 else [self.lights[light_id]]
        except IndexError:
            raise LightIdRangeError(light_id, len(self.lights)) from None

    def update(self) -> int:
        """Checks for available lights that are not lights and adds
        them to the list of lights. Optionally starts a helper
        thread for lights that require one.

        :return: number of new lights added to lights list
        """

        new_lights = []
        for info in self.available:
            for LightClass in SUPPORTED_LIGHTS:
                try:
                    new_lights.append(LightClass.from_dict(info))
                except UnknownUSBLight:
                    pass
                except USBLightInUse:
                    pass

        if new_lights:
            self.lights.extend(new_lights)
            for light in new_lights:
                try:
                    light.helper_thread.start()
                except AttributeError:
                    pass

        return len(new_lights)

    def release(self) -> None:
        """Stops all helper and effects threads, closes all lights and empties
        the `lights` property.

        Call `update` to repopulate the `lights` property and restart
        helper threads.
        """

        for light in self.lights:
            light.close()

        self.lights.clear()

    def light_on(self, light_id: Union[int, None] = -1, color: str = "green") -> None:
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
            light.stop_effect()
            light.on(rgb)

    def light_off(self, light_id: Union[int, None] = -1) -> None:
        """Turn off a light or all lights.
        
        If light_id is -1 the operation is applied to all lights.

        :param light_id: Union[int, None]

        Raises:
        - LightIdRangeError
        """

        for light in self.lights_for(light_id):
            light.stop_effect()
            light.off()

    def light_blink(
        self,
        light_id: Union[int, None] = -1,
        color: str = "red",
        speed: BlinkSpeed = BlinkSpeed.SLOW,
    ) -> None:
        """Start a light or lights blinking with the supplied color and speed.

        :param light_id: int
        :param color: str
        :param speed: BlinkSpeed
        """

        try:
            rgb = color_to_rgb(color)
        except ValueError:
            raise ColorLookupError(color) from None

        self.light_off(light_id)

        for light in self.lights_for(light_id):
            light.blink(rgb, speed.to_int())

    def apply_effect_to_light(
        self, light_id: Union[int, None], effect: Callable, *args, **kwds
    ):
        """Apply an effect function to the specified light.

        :param light_id: 
        :param effect: 
        :param args:
        :param kwds:
        """

        self.light_off(light_id)

        for light in self.lights_for(light_id):
            light.start_effect(effect)

    @contextmanager
    def operate_on(
        self,
        light_id: Union[int, None] = -1,
        turn_off_first: bool = True,
        cleanup: bool = False,
    ) -> object:
        """
        """

        if turn_off_first:
            self.light_off(light_id)

        yield self

        if cleanup:
            self.light_off(light_id)

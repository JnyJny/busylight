"""
"""

from typing import Callable, Dict, List, Tuple, Union

import hid

from . import available_lights, get_all_lights
from . import SUPPORTED_LIGHTS

from .usblight import USBLight

from ..color import color_to_rgb


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
            self._supported.append(light.name)

        return self._supported

    @property
    def available(self) -> List[Dict[str, Union[str, int]]]:
        """A list of dictionaries describing currently available lights.
        """
        return available_lights()

    @property
    def managed(self) -> List[USBLight]:
        """List of USBLight subclasses that the manager is currently
        controlling. 
        """
        try:
            return self._managed
        except AttributeError:
            pass
        self._managed = []
        return self._managed

    def lights_for(self, light_id: int = -1) -> List[USBLight]:
        """
        """
        return self.managed if light_id == -1 else [self.managed[light_id]]

    def shutdown(self, effects: bool = True, helpers: bool = False) -> None:
        """ **Not Needed** if threads are daemons
        """

    def update(self) -> int:
        """Checks for lights that are currently not managed and
        adds them to the stable of managed lights. Optionally
        starts a helper thread for lights that implement a
        `helper` method.

        :return: number of new lights added to managed list
        """
        new_lights = list(get_all_lights())

        if not new_lights:
            return

        self.managed.extend(new_lights)

        for light in new_lights:
            try:
                light.helper_thread.start()
            except AttributeError:
                pass

        return len(new_lights)

    def release(self) -> None:
        """Stops all helper and effects threads, closes all lights and empties
        the `managed` property.

        Call `update` to repopulate the `managed` property and restart
        helper threads.
        """

        for light in self.managed:
            light.close()

        self.managed.clear()

    def light_on(self, light_id: int = -1, color: str = "green") -> None:
        """Turn on a light or all lights with supplied color value.
        
        If light_id is -1 the operation is applied to all managed lights.

        :param light_id: int
        :param color: 3-tuple of red, green and blue 8-bit integers

        Raises:
        - IndexError
        """

        rgb = color_to_rgb(color)

        for light in self.lights_for(light_id):
            light.stop_effect()
            light.on(rgb)

    def light_off(self, light_id: int = -1) -> None:
        """Turn off a light or all lights.
        
        If light_id is -1 the operation is applied to all managed lights.

        :param light_id: int

        Raises:
        - IndexError
        """

        for light in self.lights_for(light_id):
            light.stop_effect()
            light.off()

    def light_blink(
        self, light_id: int = -1, color: str = "red", speed: int = 1
    ) -> None:
        """Start a light or lights blinking with the supplied color and speed.

        :param light_id: int
        :param color: str
        :param speed: int
        """

        rgb = color_to_rgb(color)

        self.light_off(light_id)

        for light in self.lights_for(light_id):
            light.blink(rgb, speed)

    def apply_effect_to_light(self, light_id: int, effect: Callable, *args, **kwds):
        """Apply an effect function to the specified light.

        :param light_id: 
        :param effect: 
        :param args:
        :param kwds:
        """

        self.light_off(light_id)
        for light in self.lights_for(light_id):
            light.start_effect(effect)

"""
"""

from threading import Thread
from typing import Callable, Dict, List, Tuple, Union

import hid

from . import available_lights, get_all_lights
from . import SUPPORTED_LIGHTS

from .usblight import USBLight

from ..color import color_to_rgb


class StoppableThread(Thread):
    """StoppableThread
    """

    def __init__(self, target: Callable, name: str, args=None, daemon: bool = None):
        """
        :param target: Callable
        :param name: str
        :param args: tuple
        :param daemon: bool
        """
        super().__init__(target=target, name=name, args=args, daemon=daemon)
        self._RUN: bool = True

    def run(self):
        """
        """
        for _ in self._target(self._args):
            if not self._RUN:
                break

    def stop(self):
        """
        """
        self._RUN = False


class LightHelperThread(StoppableThread):
    """
    """

    def __init__(self, light: USBLight):
        """
        """
        try:
            super().__init__(
                name=f"helper-{light.identifier}", target=light.helper, daemon=True
            )
        except AttributeError:
            raise ValueError(f"Light {light!s} does not implement a helper method.")
        self.light = light


class LightEffectThread(StoppableThread):
    """
    """

    def __init__(self, effect: Callable, light: USBLight):
        """
        """
        super().__init__(
            name=f"effect-{light.identifier}", target=effect, args=light, daemon=True
        )


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
            self._supported.append(f"{light.__vendor__}:{light.__name__}")

        return self._supported

    @property
    def available(self) -> List[Dict[str, Union[str, int]]]:
        """A list of dictionaries describing currently available lights.
        """
        return available_lights()

    @property
    def managed_lights(self) -> List[USBLight]:
        try:
            return self._managed_lights
        except AttributeError:
            pass
        self._managed_lights = []
        return self._managed_lights

    @property
    def helpers(self) -> Dict[str, LightHelperThread]:
        """
        """
        try:
            return self._helpers
        except AttributeError:
            pass
        self._helpers = {}
        return self._helpers

    @property
    def effects(self) -> Dict[str, LightEffectThread]:
        """
        """
        try:
            return self._effects
        except AttributeError:
            pass
        self._effects = {}
        return self._effects

    def lights_for(self, light_id: int = -1) -> List[USBLight]:
        """
        """
        return (
            self.managed_lights if light_id == -1 else [self.managed_lights[light_id]]
        )

    def shutdown(self, effects: bool = True, helpers: bool = False) -> None:
        """ **Not Needed** if threads are daemons
        """

        if effects:
            for t in self.effects:
                t.stop()

        if helpers:
            for t in self.helpers:
                t.stop()

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

        self.managed_lights.extend(new_lights)

        for light in new_lights:
            try:
                thrd = LightHelperThread(light)
                self.helpers[light.identifier] = thrd
                thrd.start()
            except ValueError:
                pass

        return len(new_lights)

    def release(self) -> None:
        """Stops all helper and effects threads, closes all lights and empties
        the `managed_lights` property.

        Call `update` to repopulate the `managed_lights` property and restart
        helper threads.
        """

        for helper in self.helpers:
            helper.stop()
        for effect in self.effects:
            effect.stop()

        for light in self.managed_lights:
            light.device.close()

        self.managed_lights.clear()

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
            light.on(rgb)

    def light_off(self, light_id: int = -1) -> None:
        """Turn off a light or all lights.
        
        If light_id is -1 the operation is applied to all managed lights.

        :param light_id: int

        Raises:
        - IndexError
        """

        for light in self.lights_for(light_id):
            running_effect = self.effects.get(light.identifier, None)
            if running_effect:
                running_effect.stop()
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
            thrd = LightEffectThread(effect, light)
            thrd.start()
            self.effects[light.identifier] = thrd

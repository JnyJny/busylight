"""Color Effects

"""

import asyncio
import time

from itertools import cycle
from typing import Callable, Dict, List, Tuple, Union

from .gradient import Gradient
from .spectrum import Spectrum

from ..lights import USBLightIOError

## Effects are called from a threading.Thread.run subclass
## that can be stopped externally. The effects functions
## need to yield ocassionlly to allow the thread to decide
## whether it has been stopped or not.


def rainbow(light: object, interval: float = 0.05) -> None:
    """Color cycle the light thru a rainbow spectrum.

    :param light: USBLight subclass
    :param interval: float
    """
    colors = [rgb for rgb in Spectrum(steps=255)]
    while True:
        for color in cycle(colors):
            try:
                light.on(color)
            except USBLightIOError:
                exit()
            yield
            time.sleep(interval)


async def rainbow_async(light: object, interval: float = 0.05) -> None:
    """Color cycle the light thru a rainbow spectrum.

    :param light: USBLight subclass
    :param interval: float
    """
    colors = [rgb for rgb in Spectrum(steps=255)]
    while True:
        for color in cycle(colors):
            try:
                light.on(color)
            except USBLightIOError:
                exit()
            await asyncio.sleep(interval)
            yield


def throbber(
    light: object, color: Tuple[int, int, int], interval: float = 0.1, sleepf=None
) -> None:
    pass


async def throbber_async(
    light: object, color: Tuple[int, int, int], interval: float = 0.1
) -> None:
    pass


def flash_lights_impressively(
    light: object, colors: List[Tuple[int, int, int]], interval: float = 0.1
) -> None:
    pass


async def flash_lights_impressively_async(
    light: object, colors: List[Tuple[int, int, int]], interval: float = 0.1
) -> None:
    pass


__all__ = [
    "Gradient",
    "Spectrum",
    "rainbow",
    "rainbow_async",
    "throbber",
    "throbber_async",
    "flash_lights_impressively",
    "flash_lights_impressively_async",
]

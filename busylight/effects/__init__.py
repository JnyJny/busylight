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


def rainbow(light: object, interval: float = 0.05, /, **kwds) -> None:
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


async def rainbow_async(light: object, interval: float = 0.05, /, **kwds) -> None:
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
            await asyncio.sleep(interval)


def pulse(
    light: object, color: Tuple[int, int, int] = None, interval: float = 0.01,
) -> None:
    """
    """
    if not color or not any(color):
        color = (255, 0, 0)

    r, g, b = color

    gradient = Gradient(color, 8, reverse=True)

    while True:
        for color in cycle(gradient):
            try:
                light.on(color)
            except USBLightIOError:
                exit()
            yield
            time.sleep(interval)


async def pulse_async(
    light: object, color: Tuple[int, int, int], interval: float = 0.1,
) -> None:
    pass


def flash_lights_impressively(
    light: object, colors: List[Tuple[int, int, int]] = None, interval: float = 0.05
) -> None:

    if not colors:
        colors = [(0xFF, 0, 0), (0, 0xFF, 0), (0, 0, 0xFF)]

    for color in cycle(colors):
        try:
            light.on(color)
        except USBLightIOError:
            exit()
        yield
        time.sleep(interval)


async def flash_lights_impressively_async(
    light: object, colors: List[Tuple[int, int, int]], interval: float = 0.1
) -> None:
    pass


__all__ = [
    "Gradient",
    "Spectrum",
    "rainbow",
    "rainbow_async",
    "pulse",
    "pulse_async",
    "flash_lights_impressively",
    "flash_lights_impressively_async",
]

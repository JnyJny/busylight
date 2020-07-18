"""Color Gradient Effect
"""
from typing import List, Tuple


def Gradient(
    start: int,
    stop: int,
    step: int,
    red=True,
    green=False,
    blue=False,
    reverse: bool = False,
) -> List[Tuple[int, int, int]]:
    """Returns a list of RBG tuples that describe a color gradient.

    The gradient starts at `start` and finishes with `stop` with `step` sized
    intervals between color tuples. If the user calls with reverse=True, the
    list is reversed and appended to itself to create a ramp up/ramp down
    effect.

    :param start: integer
    :param stop: integer
    :param step: integer
    :param red: bool
    :param green: bool
    :param blue: bool
    :param reverse: bool

    :return: List[Tuple[int, int, int]]
    """
    colors = []
    for i in range(start, stop, step):
        colors.append((i if red else 0, i if blue else 0, i if green else 0))

    if reverse:
        colors += reversed(colors)

    return colors

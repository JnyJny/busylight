"""Color Gradient Effect
"""
from typing import Generator, List, Tuple


def Gradient(
    color: Tuple[int, int, int],
    step: int = 1,
    reverse: bool = False,
) -> List[Tuple[int, int, int]]:
    """Returns a list of RGB tuples that describe a color gradient.

    :param color: Tuple[int, int, int]
    :param steps: int
    :param reverse: bool

    :return: List[Tuple[int, int, int]]
    """

    red, green, blue = color

    colors = []
    for i in range(1, 256, step):

        scale = i / 255

        r = round(scale * red)
        g = round(scale * green)
        b = round(scale * blue)
        colors.append((r, g, b))

    colors.append(color)

    if reverse:
        colors += reversed(colors)

    return colors

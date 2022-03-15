"""
"""

from typing import Generator, Tuple

from ..color import ColorTuple

FrameTuple = Tuple[ColorTuple, float]
FrameGenerator = Generator[FrameTuple, None, None]

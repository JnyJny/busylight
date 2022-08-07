""" USB Serial Light
"""


from typing import Any

import serial

from loguru import logger

from .light import Light

SerialInfo = dict[Any, Any]


class SerialLight(Light):
    """ """

    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not SerialLight

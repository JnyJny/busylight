"""
"""


from typing import Any

from loguru import logger

from .light import Light

SerialInfo = dict[Any, Any]


class SerialLight(Light):
    @classmethod
    def claims(cls, serial_info: SerialInfo) -> bool:
        pass

    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not SerialLight

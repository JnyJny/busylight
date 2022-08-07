"""
"""

from typing import Any, Union

import hid

from loguru import logger


from .light import Light


HIDInfo = dict[str, Union[bytes, str, int]]


class HIDLight(Light):
    @classmethod
    def available_lights(cls) -> list[dict[Any, Any]]:
        pass

    @classmethod
    def is_concrete(cls) -> bool:
        return cls is not HIDLight

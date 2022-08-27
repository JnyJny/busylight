"""
"""

from typing import List, Tuple, Type, TypeVar

from busylight.lights import Light, HIDLight, SerialLight

LightType = Type[Light]
LightTypes = List[LightType]


ABSTRACT_LIGHT_SUBCLASSES: LightTypes = [Light, HIDLight, SerialLight]
CONCRETE_LIGHT_SUBCLASSES: LightTypes = Light.subclasses()
ALL_LIGHT_SUBCLASSES: LightTypes = ABSTRACT_LIGHT_SUBCLASSES + CONCRETE_LIGHT_SUBCLASSES

BOGUS_DEVICE_ID: Tuple[int, int] = (0xFFFF, 0xFFFF)

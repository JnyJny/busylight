"""
"""

from contextlib import suppress
from enum import Enum
from typing import Dict, Union

from .dataframe import BlinkStickDataframe8
from .dataframe import BlinkStickDataframe16
from .dataframe import BlinkStickDataframe32
from .dataframe import BlinkStickDataframe64
from .dataframe import BlinkStickDataframe192

from .dataframe import ReportField
from .dataframe import ChannelField
from .dataframe import IndexField
from .dataframe import Color8Field


from ..usblight import USBLight
from ..statevector import StateVector


class BlinkStickIndexedLEDCommand(StateVector):
    def __init__(self):
        super().__init__(5 << 40, 48)

    report = ReportField(40, 8)
    channel = ChannelField(32, 8)
    index = IndexField(24, 8)
    red = Color8Field(16, 8)
    green = Color8Field(8, 8)
    blue = Color8Field(0, 8)


class BlinkStickUnknownVariant(Exception):
    pass


class BlinkStickVariant(int, Enum):

    BLINKSTICK = 1
    PRO = 2
    SQUARE = 0x200
    STRIP = 0x201
    NANO = 0x202
    FLEX = 0x203

    @classmethod
    def identify(cls, info: Dict[str, Union[str, int, bytes]]):
        """Identify the given USBLight's BlinkStick hardware variant.

        :return: BlinkStickVariant

        Raises:
        - BlinkStickUnknownVariant
        """

        serial_number = str(info.get("serial_number", "0.0-unknown"))
        sequence, _, version = serial_number.strip().partition("-")

        major, minor = version.split(".")

        with suppress(ValueError):
            return cls(int(major))

        with suppress(ValueError, KeyError):
            return cls(int(info["release_number"]))

        raise BlinkStickUnknownVariant(info)

    def __str__(self):

        if self.value == 1:
            return "BlinkStick"

        return f"BlinkStick {self.name.title()}"

    @property
    def nleds(self) -> int:
        """Number of LEDs supported by this BlinkStick light variant."""

        try:
            return self._nleds
        except AttributeError:
            pass

        self._nleds: int = {0x002: 192, 0x200: 8, 0x201: 8, 0x202: 2, 0x203: 32}.get(
            self.value, 1
        )
        return self._nleds

    @property
    def state(self):
        try:
            return self._state
        except AttributeError:
            pass

        if self.value in [0x200, 0x201, 0x202]:
            self._state = BlinkStickDataframe8()

        if self.value == 0x203:
            self._state = BlinkStickDataframe32()

        if self.value == 2:
            self._state = BlinkStickDataframe192()

        return self._state

"""
"""

from contextlib import suppress
from enum import Enum


from ..usblight import USBLight
from ..statevector import StateField, StateVector


class BlinkStickVariant(int, Enum):
    UNKNOWN = 0
    BLINKSTICK = 1
    PRO = 2
    SQUARE = 0x200
    STRIP = 0x201
    NANO = 0x202
    FLEX = 0x203

    @classmethod
    def identify(cls, light: USBLight):
        """Identify the given USBLight's BlinkStick hardware variant.

        :return: BlinkStickVariant
        """

        sequence, _, version = light.info["serial_number"].strip().partition("-")
        major, minor = version.split(".")

        with suppress(ValueError):
            return cls(int(major))

        with suppress(ValueError):
            return cls(int(light.info["release_number"]))

        return cls(0)

    @property
    def nleds(self) -> int:
        """Number of LEDs supported by this BlinkStick light variant."""

        try:
            return self._nleds
        except AttributeError:
            pass

        self._nleds = {0x002: 192, 0x200: 8, 0x201: 8, 0x202: 2, 0x203: 32}.get(
            self.value, 1
        )
        return self._nleds

    def __str__(self):

        if self.value == 0:
            return "Unknown Device"

        if self.value == 1:
            return "BlinkStick"

        return f"BlinkStick {self.name.title()}"


class BlinkStickReportAttribute(StateField):
    """An 8-bit feature report value."""


class BlinkStickChannelAttribute(StateField):
    """An 8-bit channel value: 0: red, 1: green, 2: blue."""


class BlinkStickIndexAttribute(StateField):
    """An 8-bit index value to specify individual LEDs."""


class BlinkStickLEDColorAttribute(StateField):
    """A 24-bit color value. Accepts an integer or 3-tuple of ints."""

    def __set__(self, obj, value):
        if isinstance(value, tuple):
            value = int.from_bytes(bytes(value), "big")
        super().__set__(obj, value)


class BlinkStickColorAttribute(StateField):
    """An 8-bit color value."""


class BlinkStickState(StateVector):
    def __init__(self):
        super().__init__(0, 208)

    report = BlinkStickReportAttribute(200, 8)
    channel = BlinkStickChannelAttribute(192, 8)
    index = BlinkStickIndexAttribute(184, 8)
    red = BlinkStickColorAttribute(176, 8)
    green = BlinkStickColorAttribute(168, 8)
    blue = BlinkStickColorAttribute(160, 8)

    led0 = BlinkStickLEDColorAttribute(168, 24)
    led1 = BlinkStickLEDColorAttribute(144, 24)
    led2 = BlinkStickLEDColorAttribute(120, 24)
    led3 = BlinkStickLEDColorAttribute(96, 24)
    led4 = BlinkStickLEDColorAttribute(72, 24)
    led5 = BlinkStickLEDColorAttribute(48, 24)
    led6 = BlinkStickLEDColorAttribute(24, 24)
    led7 = BlinkStickLEDColorAttribute(0, 24)

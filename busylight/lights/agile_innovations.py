"""support for Agile Innovations' BlinkStick family of products.
"""


from enum import Enum
from functools import partial
from time import sleep
from typing import Tuple, Union

from bitvector import BitVector, BitField

from .usblight import USBLight, USBLightAttribute
from .usblight import UnknownUSBLight
from .usblight import USBLightIOError


def _blink_effect(light: USBLight, color: Tuple[int, int, int], speed: int = 1) -> None:
    """An effects generator function that blinks a BlinkStick on and off.
    
    This generator function is intended to be used as an argument to the
    `USBLight.start_effect` method. 

    :param light: USBLight
    :param color: Tuple[int, int, int]
    :param speed: int
    """

    _SLOW = 1.0
    _MED = 0.5
    _FAST = 0.25

    interval = {1: _SLOW, 2: _MED, 3: _FAST}.get(speed, _SLOW)

    while True:
        light.on(color)
        yield
        sleep(interval)
        light.off()
        yield
        sleep(interval)


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

        try:
            return cls(int(major))
        except ValueError:
            pass

        try:
            return cls(int(light.info["release_number"]))
        except ValueError:
            pass

        return cls(0)

    @property
    def nleds(self) -> int:
        """Number of LEDs supported by this BlinkStick light variant."""

        try:
            return self._nleds
        except AttributeError:
            pass

        self._nleds = {2: 192, 0x200: 8, 0x201: 8, 0x202: 2, 0x203: 32}.get(
            self.value, 1
        )
        return self._nleds

    def __str__(self):

        if self.value == 0:
            return "Unknown Device"

        if self.value == 1:
            return "BlinkStick"

        return f"BlinkStick {self.name.title()}"


class BlinkStickReportAttribute(USBLightAttribute):
    """An 8-bit feature report value.
    """


class BlinkStickChannelAttribute(USBLightAttribute):
    """An 8-bit channel value: 0: red, 1: green, 2: blue."""


class BlinkStickIndexAttribute(USBLightAttribute):
    """An 8-bit index value to specify individual LEDs."""


class BlinkStickLEDColorAttribute(USBLightAttribute):
    """A 24-bit color value. Accepts an integer or 3-tuple of ints."""

    def __set__(self, obj, value):
        if isinstance(value, tuple):
            value = int.from_bytes(bytes(value), "big")
        super().__set__(obj, value)


class BlinkStickColorAttribute(USBLightAttribute):
    """An 8-bit color value."""


class BlinkStick(USBLight):
    """Support for Agile Innovations' BlinkStick family of USB connected lights.

    NOTE: Inital development was tested with a BlinkStick Square and is
          unlikely to work with other BlinkStick variants currently.

    The BlinkStick family of hardware is another interesting open-source
    hardware project (see ThingM for another), however it's probably the
    least capable device compared to the other supported presense lights.

    BlinkSticks variants have a differing number of LEDs available, and
    are limited to turning LEDs on with a color and turning them off
    with a color. It's up to software to drive any other desired effects
    or animations (fades, blinks, etc).  The BlinkStick's LEDs are
    individually addressable which sort of makes up for the lack of a
    programmable "blink" mode. 

    """

    VENDOR_IDS = [0x20A0]
    __vendor__ = "Agile Innovations"

    def __init__(self, vendor_id: int, product_id: int):
        """
        :param vendor_id: 16-bit int
        :param product_id: 16-bit int
        
        Raises:
        - UnknownUSBLight
        - USBLightInUse
        - USBLightNotFound
        """

        # Rough command layout
        #   R,G,B - 8 bit colors
        #   C - channel
        #   I - index
        #   GRBn - green, red, blue
        #   X - pad
        #
        # [1, R, G, B]
        # [2, ?]
        # [3, ?]
        # [4, ?]
        # [5, C, I, R, G, B]
        # [6, X, GRB0, GRB1, .. GRB7]
        # [7, X, GRB0, ..., GRB15
        # [8, X, GRB0, ..., GRB31]
        # [9, X, GRB0, ..., GRB63]

        if vendor_id not in self.VENDOR_IDS:
            raise UnknownUSBLight(vendor_id)

        super().__init__(vendor_id, product_id, 0, 208)

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

    @property
    def variant(self) -> BlinkStickVariant:
        try:
            return self._variant
        except AttributeError:
            pass

        self._variant = BlinkStickVariant.identify(self)

        return self._variant

    @property
    def name(self) -> str:
        """Concatenation of the light's vendor and product name, title-cased.
        """
        try:
            return self._name
        except AttributeError:
            pass
        self._name = str(self.variant)
        return self._name

    def impl_on(self, color: Tuple[int, int, int]) -> None:
        """"Turn the light on with the specified color.
        """
        self.set_leds(color)

    def impl_off(self) -> None:
        """Turn the light off.
        """
        self.set_leds((0, 0, 0))

    def impl_blink(self, color: Tuple[int, int, int], speed: int) -> None:
        """Turn the light on with specified color [default=red] and begin blinking.

        :param color: Tuple[int, int, int]
        :param speed: 1 == slow, 2 == medium, 3 == fast
        """

        self.start_effect(partial(_blink_effect, color=color, speed=speed))

    def set_leds(self, color: Tuple[int, int, int]):
        """
        """
        r, g, b = color
        color = g, r, b

        with self.batch_update():
            self.report = 6
            self.channel = 0
            self.led0 = color
            self.led1 = color
            self.led2 = color
            self.led3 = color
            self.led4 = color
            self.led5 = color
            self.led6 = color
            self.led7 = color

    def set_led(self, led: int, color: Tuple[int, int, int]):
        """
        """
        with self.batch_update():
            self.reset()
            self.report = 5
            self.channel = 0
            self.index = led
            self.led0 = color

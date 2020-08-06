"""support for BlinkStick products.
"""


from enum import Enum
from functools import partial
from time import sleep
from typing import Tuple, Union

from bitvector import BitVector, BitField

from .usblight import USBLight, USBLightAttribute
from .usblight import UnknownUSBLight
from .usblight import USBLightIOError


def _blink(light: USBLight, color: Tuple[int, int, int], speed: int = 1) -> None:
    """
    """

    interval = {1: 0.5, 2: 0.3, 1: 0.1}.get(speed, 0.5)

    while True:
        light.on(color)
        yield
        sleep(interval)

        light.off()
        yield
        sleep(interval)


class Report(int, Enum):
    RGB = 1
    CHIDX = 5
    LEDS8 = 6
    LEDS16 = 7
    LESD32 = 8
    LEDS64 = 9


class BlinkStickVariant(int, Enum):
    UNKNOWN = 0
    BLINKSTICK = 1
    PRO = 2
    SQUARE = 0x200
    STRIP = 0x201
    NANO = 0x202
    FLEX = 0x203

    @classmethod
    def identify(cls, blinkstick: object):
        """
        """

        sequence, _, version = blinkstick.info["serial_number"].strip().partition("-")
        major, minor = version.split(".")

        try:
            return cls(int(major))
        except ValueError:
            pass

        try:
            return cls(int(blinkstick.info["release_number"]))
        except ValueError:
            pass

        return cls(0)

    def __str__(self):

        if self.value == 0:
            return "Unknown BlinkStick"

        if self.value == 1:
            return "BlinkStick"

        return f"BlinkStick {self.name.title()}"


class BlinkStickReportAttribute(USBLightAttribute):
    """
    """


class BlinkStickChannelAttribute(USBLightAttribute):
    """"""


class BlinkStickIndexAttribute(USBLightAttribute):
    """"""


class BlinkStickLEDColorAttribute(USBLightAttribute):
    """An 24-bit color value."""

    def __set__(self, obj, value):
        if isinstance(value, tuple):
            value = int.from_bytes(bytes(value), "big")
        super().__set__(obj, value)


class BlinkStickColorAttribute(USBLightAttribute):
    """An 8-bit color value."""


class BlinkStick(USBLight):

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

    @property
    def nleds(self) -> int:
        """Number of LEDs supported by light variant."""

        try:
            return self._nleds
        except AttributeError:
            pass

        self._nleds = {2: 192, 0x200: 8, 0x201: 8, 0x202: 2, 0x203: 32}.get(
            self.variant.value, 1
        )
        return self._nleds

    def write(self):
        """
        """
        nbytes = self.device.write(self.bytes)
        if nbytes != len(self.bytes):
            raise USBLightIOError(self, nbytes)

    def on(self, color: Tuple[int, int, int] = None) -> None:
        """
        """

        if color is None or not any(color):
            color = (0, 255, 0)

        self.bs_set_leds(color)

    def off(self) -> None:
        """
        """
        self.bs_set_leds((0, 0, 0))

    def blink(self, color: Tuple[int, int, int], speed: int = 1) -> None:
        """
        """

        interval = {1: 1, 2: 0.5, 3: 0.25}.get(speed, 1)

        try:
            while True:
                self.on(color)
                sleep(interval)
                self.off()
                sleep(interval)
        except KeyboardInterrupt:
            pass

    def bs_set_leds(self, color: Tuple[int, int, int]):

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

    def bs_set_led(self, led: int, color: Tuple[int, int, int]):

        with self.batch_update():
            self.reset()
            self.report = 5
            self.channel = 0
            self.index = led
            self.led0 = color

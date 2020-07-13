"""Embrava BlyncLight support.
"""

from typing import Tuple

from .usblight import USBLight, UnknownUSBLight
from .usblight import USBLightAttribute
from .usblight import USBLightImmediateAttribute
from .usblight import USBLightReadOnlyAttribute


class BlyncLightCommandHeader(USBLightReadOnlyAttribute):
    """A constant 16-bit field with zero value."""


class BlyncLightColor(USBLightImmediateAttribute):
    """An 8-bit color."""


class BlyncLightOff(USBLightImmediateAttribute):
    """Toggle the light off and on: 1 == off, 0 == on."""


class BlyncLightDim(USBLightImmediateAttribute):
    """Toggle the light from bright to dim. bright == 0, dim == 1."""


class BlyncLightFlash(USBLightImmediateAttribute):
    """Toggle the light from steady to flash mode."""


class BlyncLightSpeed(USBLightImmediateAttribute):
    """A four bit field that specifies the flash speed."""


class BlyncLightRepeat(USBLightImmediateAttribute):
    """Toggle tune repeat: 0 once, 1 repeat"""


class BlyncLightPlay(USBLightImmediateAttribute):
    """Toggle playing selected tune."""


class BlyncLightMusic(USBLightImmediateAttribute):
    """Select a tune in firmware: 0 - 10"""


class BlyncLightMute(USBLightImmediateAttribute):
    """Toggle muting the tune being played. 0 == play, 1 == mute."""


class BlyncLightVolume(USBLightImmediateAttribute):
    """Volume of the tune when played: 0 - 10"""


class BlyncLightCommandFooter(USBLightReadOnlyAttribute):
    """A 16-bit constant field with value 0xFF22."""


class BlyncLight(USBLight):

    VENDOR_IDS = [0x2C0D, 0x03E5]

    __vendor__ = "Embrava"

    def __init__(self, vendor_id: int, product_id: int):
        """An Embrava Blynclight device.

        :param vendor_id: 16-bit int
        :param product_id: 16-bit int
        
        Raises:
        - UnknownUSBLight
        - USBLightInUse
        - USBLightNotFound
        """

        if vendor_id not in self.VENDOR_IDS:
            raise UnknownUSBLight(vendor_id)

        super().__init__(vendor_id, product_id, 0x00000000090080FF22, 72)
        self.immediate_mode = True

    header = BlyncLightCommandHeader(64, 8)
    red = BlyncLightColor(56, 8)
    blue = BlyncLightColor(48, 8)
    green = BlyncLightColor(40, 8)
    _off = BlyncLightOff(32, 1)
    dim = BlyncLightDim(33, 1)
    flash = BlyncLightFlash(34, 1)
    speed = BlyncLightSpeed(35, 3)
    repeat = BlyncLightRepeat(29, 1)
    play = BlyncLightPlay(28, 1)
    music = BlyncLightMusic(24, 4)
    mute = BlyncLightMute(23, 1)
    volume = BlyncLightVolume(18, 4)
    footer = BlyncLightCommandFooter(0, 16)

    def on(self, color: Tuple[int, int, int] = None) -> None:
        """Turn the light on with the specified color [default=green].
        """
        with self.updates_paused():
            self.reset()
            if color:
                self.color = color
            if not any(self.color):
                self.green = 255
            self.flash = 0
            self._off = 0

    def off(self) -> None:
        """Turn the light off.
        """
        with self.updates_paused():
            self.reset()
            self._off = 1

    def blink(self, color: Tuple[int, int, int] = None, speed: int = 1) -> None:
        """Turn the light on with specified color [default=red] and begin blinking.

        :param color: Tuple[int, int, int]
        :param speed: 1 == slow, 2 == medium, 3 == fast
        """
        with self.updates_paused():

            self.color = color or (255, 0, 0)

            if speed <= 0:
                self.flash = 0
                self.speed = 1
                self._off = 1
            else:
                self.flash = 1
                self.speed = 1 << (speed - 1)
                if self.speed == 0:
                    self.speed = 1
                self._off = 0

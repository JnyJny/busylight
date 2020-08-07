"""Embrava Blynclight support.

"""

from typing import Tuple

from .usblight import USBLight, UnknownUSBLight
from .usblight import USBLightAttribute
from .usblight import USBLightReadOnlyAttribute

## The following data descriptor class definitions
## exist to provide docstrings for the individual
## fields declared in the Blynclight class.


class BlynclightCommandHeader(USBLightReadOnlyAttribute):
    """A constant 16-bit field with zero value."""


class BlynclightColor(USBLightAttribute):
    """An 8-bit color."""


class BlynclightOff(USBLightAttribute):
    """Toggle the light off and on: 1 == off, 0 == on."""


class BlynclightDim(USBLightAttribute):
    """Toggle the light from bright to dim. bright == 0, dim == 1."""


class BlynclightFlash(USBLightAttribute):
    """Toggle the light from steady to flash mode."""


class BlynclightSpeed(USBLightAttribute):
    """A four bit field that specifies the flash speed."""


class BlynclightRepeat(USBLightAttribute):
    """Toggle tune repeat: 0 once, 1 repeat"""


class BlynclightPlay(USBLightAttribute):
    """Toggle playing selected tune."""


class BlynclightMusic(USBLightAttribute):
    """Select a tune in firmware: 0 - 10"""


class BlynclightMute(USBLightAttribute):
    """Toggle muting the tune being played. 0 == play, 1 == mute."""


class BlynclightVolume(USBLightAttribute):
    """Volume of the tune when played: 0 - 10"""


class BlynclightCommandFooter(USBLightReadOnlyAttribute):
    """A 16-bit constant field with value 0xFF22."""


class Blynclight(USBLight):
    """Support for the Embrava Blynclight family of devices.

    Blinklights are controlled by writing a nine-byte buffer
    to the device:

    header: 8 bits  must be zeros
       red: 8 bits
      blue: 8 bits
     green: 8 bits
       off: 1 bit   turns light off if set
       dim: 1 bit   dims light if set
     flash: 1 bit   enables flash mode
     speed: 3 bits  valid speeds: 0x1 0x2 0x4
    repeat: 1 bit   enables music repeat if set
      play: 1 bit   starts selected music if set
     music: 4 bits  selects firmware resident music to play
      mute: 1 bit   mutes playing music if set
    volume: 4 bits  sets music volume
    footer: 16 bits must be 0xff22

    Tested Devices:
    - BLYNCUSB30   Blynclight
    - BLYNCUSB40S  Blynclight Plus
    
    Reported Working:
    - BLMINI40     Blynclight Mini
    """

    VENDOR_IDS = [0x2C0D, 0x03E5]
    __vendor__ = "Embrava"

    def __init__(self, vendor_id: int, product_id: int):
        """
        :param vendor_id: 16-bit int
        :param product_id: 16-bit int
        
        Raises:
        - UnknownUSBLight
        - USBLightInUse
        - USBLightNotFound
        """
        # Asserted: _off, speed, mute
        super().__init__(vendor_id, product_id, 0x00000000090080FF22, 72)

    header = BlynclightCommandHeader(64, 8)
    red = BlynclightColor(56, 8)
    blue = BlynclightColor(48, 8)
    green = BlynclightColor(40, 8)
    _off = BlynclightOff(32, 1)
    dim = BlynclightDim(33, 1)
    flash = BlynclightFlash(34, 1)
    speed = BlynclightSpeed(35, 3)
    repeat = BlynclightRepeat(29, 1)
    play = BlynclightPlay(28, 1)
    music = BlynclightMusic(24, 4)
    mute = BlynclightMute(23, 1)
    volume = BlynclightVolume(18, 4)
    footer = BlynclightCommandFooter(0, 16)

    def impl_on(self, color: Tuple[int, int, int], dim: bool = False) -> None:
        """Device specific on.
        """

        with self.batch_update():
            self.reset()
            self.color = color
            self.dim = dim
            self._off = 0

    def impl_off(self) -> None:
        """Device specific off
        """

        with self.batch_update():
            self._off = 1

    def impl_blink(self, color: Tuple[int, int, int], speed: int = 1) -> None:
        """Device specific blink
        """

        with self.batch_update():
            self.color = color
            self.flash = 1
            self.speed = 1 << (speed - 1)
            if self.speed == 0:
                self.speed = 1
            self._off = 0

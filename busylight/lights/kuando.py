"""Kuanda BusyLight support.
"""


from enum import Enum
from math import log
from typing import List, Tuple

from bitvector import BitVector, BitField
from functools import lru_cache

from .usblight import USBLight, UnknownUSBLight
from .usblight import USBLightAttribute


@lru_cache(maxsize=255)
def gamma_correct(value: int, step: int = 255) -> int:
    return round((log(1 + value) / 5.545) * step)


class RingTones(int, Enum):
    OpenOffice = 136
    Quiet = 144
    Funky = 152
    FairyTale = 160
    KuandoTrain = 168
    TelephoneNordic = 176
    TelephoneOriginal = 184
    TelephonePickMeUp = 192
    Buzz = 216


class Step(BitVector):
    def __init__(self, value: int = 0):
        super().__init__(value, size=64)

    cmd = BitField(56, 8)
    repeat = BitField(48, 8)
    red = BitField(40, 8)
    green = BitField(32, 8)
    blue = BitField(24, 8)
    on_duration = BitField(16, 8)
    off_duration = BitField(8, 8)
    update = BitField(7, 1)
    ringtone = BitField(3, 4)
    volume = BitField(0, 3)

    def keepalive(self, timeout: int) -> None:
        """
        """
        self.cmd = (1 << 8) | (timeout & 0xF)

    def start_bootloader(self) -> None:
        """
        """
        self.cmd = 1 << 7

    def reset(self) -> None:
        """
        """
        self.cmd = 1 << 6

    def jump_to_step(self, step: int) -> None:
        """
        """
        self.cmd = (1 << 5) | (step & 0x3)


class BusyLight(USBLight):

    VENDOR_IDS = [0x27BB]
    __vendor__ = "Kuando"

    def __init__(self, vendor_id: int, product_id: int):
        """A Kuando BusyLight device.

        :param vendor_id: 16-bit int
        :param product_id: 16-bit int

        Raises:
        - UnknownUSBLight
        - USBLightInUse
        - USBLightNotFound
        """

        if vendor_id not in self.VENDOR_IDS:
            raise UnknownUSBLight(vendor_id)

        super().__init__(vendor_id, product_id, 0, 512)
        self.immediate_mode = True

    step0 = BitField(448, 64)
    step1 = BitField(384, 64)
    step2 = BitField(320, 64)
    step3 = BitField(256, 64)
    step4 = BitField(192, 64)
    step5 = BitField(128, 64)
    step6 = BitField(64, 64)

    sensitivity = BitField(56, 8)
    timeout = BitField(48, 8)
    trigger = BitField(40, 8)
    pad = BitField(16, 24)  # set to 0xff
    chksum = BitField(0, 16)

    def update(self, flush: bool = False) -> None:
        """
        """
        # compute checksum
        super().update(flush)

    def on(self, color: Tuple[int, int, int] = None) -> None:
        """Turn the light own the specified color [default=green].
        """

        with self.updates_paused():
            pass

    def off(self) -> None:
        """Turn the light off.
        """
        with self.updates_paused():
            pass

    def blink(self, color: Tuple[int, int, int] = None, speed: int = 1) -> None:
        """Turn the light on with specified color [default=red] and begin blinking.
        
        :param color: Tuple[int, int, int]
        :param speed: 1 == slow, 2 == medium, 3 == fast
        """

        with self.updates_paused():
            pass

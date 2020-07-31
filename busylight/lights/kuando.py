"""Kuando BusyLight support.
"""

import threading

from enum import Enum
from time import sleep
from typing import List, Tuple

from bitvector import BitVector, BitField

from .usblight import USBLight, UnknownUSBLight
from .usblight import USBLightAttribute


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


class StepCommand(int, Enum):
    KEEP_ALIVE = 1 << 3
    BOOT_LOADER = 1 << 2
    RESET = 1 << 1
    JUMP = 1 << 0


class StepCmdHiField(BitField):
    """
    """


class StepCmdLoField(BitField):
    """
    """


class StepTargetField(BitField):
    """
    """


class StepTimeoutField(BitField):
    """
    """


class StepRepeatField(BitField):
    """
    """


class StepColorField(BitField):
    """
    """


class StepDutyCycleField(BitField):
    """
    """


class StepUpdateField(BitField):
    """
    """


class StepRingtoneField(BitField):
    """
    """


class StepVolumeField(BitField):
    """
    """


class StepField(USBLightAttribute):
    """
    """


class BusyLightSensitivityField(USBLightAttribute):
    """
    """


class BusyLightTimeoutField(USBLightAttribute):
    """
    """


class BusyLightTriggerField(USBLightAttribute):
    """
    """


class BusyLightPadBytes(USBLightAttribute):
    """
    """


class BusyLightChecksumField(USBLightAttribute):
    """
    """


class Step(BitVector):
    @classmethod
    def jump_to(cls, target: int):
        default = ((StepCommand.JUMP << 4) | (target & 0x7)) << 56
        return cls(default=default)

    @classmethod
    def keep_alive(cls, timeout: int):
        default = ((StepCommand.KEEP_ALIVE << 4) | (timeout & 0xF)) << 56
        return cls(default=default)

    @classmethod
    def hardreset(cls):
        return cls(default=(StepCommand.RESET << 60))

    @classmethod
    def boot_loader(cls):
        return cls(default=(StepCommand.BOOT_LOADER << 60))

    def __init__(self, default: int = 0):
        super().__init__(default, size=64)

    cmd0 = StepCmdHiField(60, 4)
    cmd1 = StepCmdLoField(56, 4)
    target = StepTargetField(56, 4)
    timeout = StepTimeoutField(56, 4)

    repeat = StepRepeatField(48, 8)
    red = StepColorField(40, 8)
    green = StepColorField(32, 8)
    blue = StepColorField(24, 8)
    dc_on = StepDutyCycleField(16, 8)
    dc_off = StepDutyCycleField(8, 8)
    update = StepUpdateField(7, 1)
    ringtone = StepRingtoneField(3, 4)
    volume = StepVolumeField(0, 3)

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, new_value: Tuple[int, int, int]) -> None:
        self.red, self.green, self.blue = new_value


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
        super().__init__(vendor_id, product_id, 0x00FF_FFFF_0000, 512)

    step0 = StepField(448, 64)
    step1 = StepField(384, 64)
    step2 = StepField(320, 64)
    step3 = StepField(256, 64)
    step4 = StepField(192, 64)
    step5 = StepField(128, 64)
    step6 = StepField(64, 64)
    final = StepField(0, 64)

    sensitivity = BusyLightSensitivityField(56, 8)
    timeout = BusyLightTimeoutField(48, 8)
    trigger = BusyLightTriggerField(40, 8)
    padbytes = BusyLightPadBytes(16, 24)
    chksum = BusyLightChecksumField(0, 16)

    def __debug_str__(self):
        return "\n".join(
            [
                "====================",
                str(self),
                "====================",
                f"00: {self.step0:016x}",
                f"01: {self.step1:016x}",
                f"02: {self.step2:016x}",
                f"03: {self.step3:016x}",
                f"04: {self.step4:016x}",
                f"05: {self.step5:016x}",
                f"06: {self.step6:016x}",
                "--------------------",
                f"07: {self.final:016x}",
            ]
        )

    def helper(self) -> None:
        """A loop that sends a keepalive message.

        This generator function is intended to be used in
        a busylight.effects.thread.EffectThread. 
        """
        timeout = 0xF
        keepalive = Step.keep_alive(timeout).value
        interval = timeout // 2
        while True:
            self.step0 = keepalive
            try:
                self.write()
            except USBLightIOError:
                break
            yield
            sleep(interval)

    def write(self) -> int:
        """Write the in-memory state of the device to hardare.

        The Kuando BusyLight requires a checksum for valid
        control packets, which is computed just prior to the
        I/O operation.

        :return: int number of bytes written
        Raises
        - USBLightIOError
        """
        self.chksum = sum(self.bytes[:-2])

        retval = self.device.write(self.bytes)
        if retval != len(self.bytes):
            raise USBLightIOError(self, retval)

    def on(self, color: Tuple[int, int, int] = None, duration: int = 0) -> None:
        """Turn the light on with the specified color [default=green].

        Raises
        - USBLightIOError
        """
        self.bl_on(color or (0, 255, 0))

    def off(self) -> None:
        """Turn the light off.

        Raises
        - USBLightIOError
        """
        self.bl_on((0, 0, 0))

    def blink(self, color: Tuple[int, int, int] = None, speed: int = 1) -> None:
        """Turn the light on with specified color [default=red] and begin blinking.
        
        :param color: Tuple[int, int, int]
        :param speed: 1 == slow, 2 == medium, 3 == fast

        Raises
        - USBLightIOError
        """
        self.bl_blink(color or (255, 0, 0), speed)

    def bl_on(self, color: Tuple[int, int, int]) -> None:
        """Turn the BusyLight on with the specified color. 
        
        :param color: Tuple[int, int, int]

        Raises
        - USBLightIOError
        """

        step = Step.jump_to(0)
        step.color = color
        step.update = 1

        with self.batch_update():
            self.reset()
            self.step0 = step.value

    def bl_blink(self, color: Tuple[int, int, int], speed: int):
        """

        :param color: Tuple[int, int, int]
        :param speed: int

        Raises
        - USBLightIOError
        """

        step = Step.jump_to(0)
        step.color = color
        step.repeat = 1
        step.update = 1
        step.dc_on = 10 // speed
        step.dc_off = 10 // speed

        with self.batch_update():
            self.reset()
            self.step0 = step.value

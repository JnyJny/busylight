"""
"""

from enum import Enum
from threading import Lock
from typing import List, Tuple

from ..statevector import StateField, StateVector


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


class OpCode(int, Enum):
    KEEP_ALIVE = 0x8
    BOOT_LOADER = 0x4
    RESET = 0x2
    JUMP = 0x1


class CommandField(StateField):
    """An 8-bit command field."""


class RepeatField(StateField):
    """An 8-bit repeat field."""


class ColorField(StateField):
    """An 8-bit color value."""


class DutyCycleField(StateField):
    """An 8-bit duty cycle value."""


class UpdateField(StateField):
    """A 1-bit update field."""


class RingtoneField(StateField):
    """A 4-bit ringtone value."""


class VolumeField(StateField):
    """A 3-bit volume value."""


class TimeoutField(StateField):
    """A 4-bit timeout value."""


class TargetField(StateField):
    """A 4-bit jump target value."""


class BaseInstruction(StateVector):
    def __init__(self, value):
        super().__init__(value, 64)
        self.lock = Lock()

    cmd0 = CommandField(60, 4)
    cmd1 = CommandField(56, 4)
    repeat = RepeatField(48, 8)
    red = ColorField(40, 8)
    green = ColorField(32, 8)
    blue = ColorField(24, 8)
    dc_on = DutyCycleField(16, 8)
    dc_off = DutyCycleField(8, 8)
    update = UpdateField(7, 1)
    ringtone = RingtoneField(3, 4)
    volume = VolumeField(0, 3)

    def __str__(self):
        return "\n".join(
            [
                "-------------------------",
                f" value: {self.value:016x}",
                f"  cmd0: {self.cmd0:02x}",
                f"  cmd1: {self.cmd1:02x}",
                f"repeat: {self.repeat:02x}",
                f"   red: {self.red:02x}",
                f" green: {self.green:02x}",
                f"  blue: {self.blue:02x}",
                f" dc on: {self.dc_on:02x}",
                f"dc off: {self.dc_off:02x}",
                f"update: {bool(self.update)}",
                f"  ring: {self.ringtone:02x}",
                f"volume: {self.volume:02x}",
            ]
        )

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, values: Tuple[int, int, int]) -> None:
        self.red, self.green, self.blue = values


class InstructionJump(BaseInstruction):
    def __init__(self, target: int):
        super().__init__(0)
        self.cmd0 = OpCode.JUMP
        self.cmd1 = target

    target = TargetField(56, 4)


class InstructionKeepAlive(BaseInstruction):
    def _init__(self, timeout: int):
        super().__init__(0)
        self.cmd0 = OpCode.KEEP_ALIVE
        self.cmd1 = timeout & 0xf

    timeout = TimeoutField(56, 4)


class InstructionHardReset(BaseInstruction):
    def _init__(self):
        super().__init__(0)
        self.cmd0 = OpCode.RESET


class InstructionField(StateField):
    """A 64-bit instruction word."""


class CheckSumField(StateField):
    """An 8-bit checksum value."""


class BusyLightState(StateVector):
    def __init__(self):
        super().__init__(0x00FF_FFFF_0000, 512)
        self.line7_mask = 0x00FF_FFFF_0000

    line0 = InstructionField(448, 64)
    line1 = InstructionField(384, 64)
    line2 = InstructionField(320, 64)
    line3 = InstructionField(256, 64)
    line4 = InstructionField(192, 64)
    line5 = InstructionField(128, 64)
    line6 = InstructionField(64, 64)
    line7 = InstructionField(0, 64)

    sensitivity = StateField(56, 8)
    timeout = StateField(48, 8)
    trigger = StateField(40, 8)
    padbytes = StateField(16, 24)
    chksum = CheckSumField(0, 16)

    def dump(self):
        return "\n".join([f"{n}: {i:016x}" for n, i in enumerate(self.instructions)])

    @property
    def instructions(self) -> List[int]:
        return [
            self.line0,
            self.line1,
            self.line2,
            self.line3,
            self.line4,
            self.line5,
            self.line6,
            self.line7,
        ]

    def __bytes__(self):
        self.chksum = sum(self.bytes[:-2])
        return self.bytes

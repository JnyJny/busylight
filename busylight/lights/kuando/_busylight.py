"""
"""

from enum import IntEnum
from typing import Tuple

from bitvector import BitField, BitVector


class Ring(IntEnum):
    Off = 0
    OpenOffice = 136
    Quiet = 144
    Funky = 152
    FairyTale = 160
    KuandoTrain = 168
    TelephoneNordic = 176
    TelephoneOriginal = 184
    TelephonePickMeUp = 192
    Buzz = 216


class OpCode(IntEnum):
    Jump = 0x1
    Reset = 0x2
    Boot = 0x4
    KeepAlive = 0x8


class CommandField(BitField):
    """An 8-bit command field."""


class RepeatField(BitField):
    """An 8-bit repeat field."""


class ColorField(BitField):
    """An 8-bit color value."""


class DutyCycleField(BitField):
    """An 8-bit duty cycle value, tenth's of a second"""


class UpdateField(BitField):
    """A 1-bit update field."""


class RingtoneField(BitField):
    """A 4-bit ringtone value."""


class VolumeField(BitField):
    """A 3-bit volume value."""


class TimeoutField(BitField):
    """A 4-bit timeout value."""


class TargetField(BitField):
    """A 4-bit jump target value."""


class Instruction(BitVector):
    @classmethod
    def Jump(
        cls,
        target: int = 0,
        color: Tuple[int, int, int] = None,
        repeat: int = 0,
        on_time: int = 0,
        off_time: int = 0,
        update: int = 0,
        ringtone: Ring = Ring.Off,
        volume: int = 0,
    ) -> "Instruction":
        """Constructs a Jump instruction and returns it.

        :target: 3-bit integer instruction line number
        :repeat: 8-bit integer
        :color: 8-bit integer 3-tuple of red, green, blue values
        :on_time: 8-bit fade in value in 0.1 second steps
        :off_time: 8-bit fade out value in 0.1 second steps
        :update: 1-bit value indicating validity of ringtone and volume
        :ringtone: 4-bit Ring enumeration value
        :volume: 3-bit integer volume
        :return: Instruction
        """
        instruction = cls()
        instruction.cmd_hi = OpCode.Jump
        instruction.cmd_lo = target & 0x07
        instruction.repeat = repeat
        instruction.dc_on = on_time
        instruction.dc_off = off_time
        instruction.update = update
        instruction.ringtone = ringtone
        instruction.volume = volume
        instruction.color = color or (0, 0, 0)
        return instruction

    @classmethod
    def Reset(cls) -> "Instruction":
        """Constructs a Reset Instruction and returns it.

        :return: Instruction
        """
        instruction = cls()
        instruction.cmd_hi = OpCode.Reset
        return instruction

    @classmethod
    def Boot(cls) -> "Instruction":
        """Constructs a Reset Instruction and returns it.

        :return: Instruction
        """

        instruction = cls()
        instruction.cmd_hi = OpCode.Boot
        return instruction

    @classmethod
    def KeepAlive(cls, timeout: int) -> "Instruction":
        """Constructs a KeepAlive Instruction and returns it.

        :timeout: 4-bit integer seconds
        :return: Instruction
        """
        instruction = cls()
        instruction.cmd_hi = OpCode.KeepAlive
        instruction.cmd_lo = timeout & 0xF
        return instruction

    def __init__(self):
        super().__init__(0, 64)

    cmd = CommandField(56, 8)
    cmd_hi = CommandField(60, 4)
    cmd_lo = CommandField(56, 4)
    repeat = RepeatField(48, 8)
    red = ColorField(40, 8)
    green = ColorField(32, 8)
    blue = ColorField(24, 8)
    dc_on = DutyCycleField(16, 8)
    dc_off = DutyCycleField(8, 8)
    update = UpdateField(7, 1)
    ringtone = RingtoneField(3, 4)
    volume = VolumeField(0, 3)

    def reset(self) -> None:
        self.value = 0

    def __repr__(self):
        return f"{type(self).__name__}(value={self.value:016x})"

    @property
    def color(self) -> Tuple[int, int, int]:
        r, g, b = map(
            lambda v: int((v / 100) * 0xFF), (self.red, self.green, self.blue)
        )
        return (r, g, b)

    @color.setter
    def color(self, color: Tuple[int, int, int]) -> None:
        self.red, self.green, self.blue = map(lambda v: int((v / 255) * 100), color)


class InstructionField(BitField):
    """A 64-bit instruction word."""


class CheckSumField(BitField):
    """An 8-bit checksum value."""


class CommandBuffer(BitVector):
    def __init__(self):
        super().__init__(0x00FF_FFFF_0000, 512)
        self.default = 0x00FF_FFFF_0000

    line0 = InstructionField(448, 64)
    line1 = InstructionField(384, 64)
    line2 = InstructionField(320, 64)
    line3 = InstructionField(256, 64)
    line4 = InstructionField(192, 64)
    line5 = InstructionField(128, 64)
    line6 = InstructionField(64, 64)
    line7 = InstructionField(0, 64)

    # the following are aliases into line7
    sensitivity = BitField(56, 8)
    timeout = BitField(48, 8)
    trigger = BitField(40, 8)
    padbytes = BitField(16, 24)
    checksum = CheckSumField(0, 16)

    def __bytes__(self):
        self.checksum = sum(self.bytes[:-2])
        return self.bytes

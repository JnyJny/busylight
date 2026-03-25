"""Kuando Busylight command classes.

This module defines the Step and Footer classes that form the core command
structure for Kuando Busylight devices. Each Step represents a single
instruction in the device's execution sequence.
"""

from busylight_core.word import BitField, Word

from .enums import OpCode, Ring
from .fields import (
    BlueField,
    BodyField,
    ChecksumField,
    DutyCycleOffField,
    DutyCycleOnField,
    GreenField,
    OpCodeField,
    OperandField,
    RedField,
    RepeatField,
    RingtoneField,
    SensitivityField,
    TimeoutField,
    TriggerField,
    UpdateBit,
    VolumeField,
)


class Step(Word):
    """A single command step for Kuando Busylight devices.

    The Step class represents one instruction in the device's command sequence.
    Each device supports up to 7 steps that can control LED colors, timing,
    ringtones, and other device behaviors.
    """

    def __init__(self) -> None:
        super().__init__(0, 64)

    def keep_alive(self, timeout: int) -> None:
        """Configure the step as a KeepAlive with timeout in seconds."""
        self.opcode = OpCode.KeepAlive
        self.operand = timeout & 0xF
        self.body = 0

    def boot(self) -> None:
        """Configure the step as a Boot instruction."""
        self.opcode = OpCode.Boot
        self.operand = 0
        self.body = 0

    def reset(self) -> None:
        """Configure the step as a Reset instruction."""
        self.opcode = OpCode.Reset
        self.operand = 0
        self.body = 0

    def jump(
        self,
        color: tuple[int, int, int],
        target: int = 0,
        repeat: int = 0,
        on_time: int = 0,
        off_time: int = 0,
        update: int = 0,
        ringtone: Ring = Ring.Off,
        volume: int = 0,
    ) -> None:
        """Configure the step as a Jump instruction."""
        self.opcode = OpCode.Jump
        self.operand = target & 0xF
        self.repeat = repeat & 0xFF
        self.color = color
        self.duty_cycle_on = on_time & 0xFF
        self.duty_cycle_off = off_time & 0xFF
        self.update = update & 0x1
        self.ringtone = ringtone & 0xF
        self.volume = volume & 0x3

    @property
    def color(self) -> tuple[int, int, int]:
        """Get the current RGB color as a tuple."""
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, color: tuple[int, int, int]) -> None:
        self.red, self.green, self.blue = color

    opcode = OpCodeField()
    operand = OperandField()
    body = BodyField()
    repeat = RepeatField()
    red = RedField()
    green = GreenField()
    blue = BlueField()
    duty_cycle_on = DutyCycleOnField()
    duty_cycle_off = DutyCycleOffField()
    update = UpdateBit()
    ringtone = RingtoneField()
    volume = VolumeField()


class Footer(Step):
    """Command footer with checksum and device-specific fields.

    The Footer extends Step with additional fields specific to command
    validation and device configuration. It includes a checksum field
    that ensures command integrity.
    """

    def __init__(self) -> None:
        super().__init__()
        self.checksum = 0
        self.pad = 0xFFF

    sensitivity = SensitivityField()
    timeout = TimeoutField()
    trigger = TriggerField()
    pad = BitField(16, 24)
    checksum = ChecksumField()

"""Kuando Busylight device state management.

This module defines the State class that manages the complete command
sequence for Kuando Busylight devices, including the execution steps
and command footer.
"""

import struct

from .commands import Footer, Step


class State:
    """Complete device state for Kuando Busylight commands.

    The State class manages the full command sequence sent to Kuando devices.
    It consists of 7 execution steps and a footer with checksum validation.
    The state is serialized to bytes for transmission to the hardware.
    """

    def __init__(self) -> None:
        self.steps = [Step() for _ in range(7)]
        self.footer = Footer()
        self.struct = struct.Struct("!8Q")

    def __bytes__(self) -> bytes:
        self.footer.checksum = sum(bytes(self.footer)[:-2])
        for step in self.steps:
            self.footer.checksum += sum(bytes(step))

        return self.struct.pack(
            *[step.value for step in self.steps],
            self.footer.value,
        )

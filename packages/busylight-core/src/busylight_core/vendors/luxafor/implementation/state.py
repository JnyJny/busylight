"""Luxafor Flag device state management.

This module defines the State class that manages command construction
for Luxafor Flag devices, including color control, effects, and
pattern selection.
"""

from loguru import logger

from .enums import LEDS, Command, Pattern, Wave


class State:
    """Complete device state for Luxafor Flag commands.

    The State class manages command construction for Luxafor devices.
    It supports various commands including solid colors, fade effects,
    strobe patterns, wave effects, and built-in patterns.
    """

    def __init__(self) -> None:
        """Initialize state with default values."""
        self.command = Command.Color
        self.leds = LEDS.All
        self.fade = 0
        self.repeat = 0
        self.pattern = Pattern.Off
        self.wave = Wave.Off
        self.color = (0, 0, 0)

    def __bytes__(self) -> bytes:
        """Convert state to bytes for device communication.

        Serializes the current state into the appropriate byte sequence
        based on the selected command type. Different commands require
        different parameter layouts.

        :return: Byte sequence for device communication
        :raises ValueError: If the command type is not supported
        """
        match self.command:
            case Command.Color:
                return bytes([self.command, self.leds, *self.color])
            case Command.Fade:
                return bytes(
                    [self.command, self.leds, *self.color, self.fade, self.repeat]
                )
            case _:
                pass

        logger.debug(f"Unsupported command: {self.command}")
        msg = f"Unsupported command: {self.command}"
        raise ValueError(msg)

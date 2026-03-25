"""ThingM Blink(1) enumerations.

This module defines the enumerations used by ThingM Blink(1) devices for
actions, LED selection, and report types.
"""

from enum import IntEnum


class Action(IntEnum):
    """Action enumeration for ThingM Blink(1) device commands.

    Defines the available actions that can be performed on Blink(1) devices.
    Each action corresponds to a specific ASCII character that the device
    firmware recognizes.
    """

    FadeColor = ord("c")
    SetColor = ord("n")
    ReadColor = ord("r")
    ServerTickle = ord("D")
    PlayLoop = ord("p")
    PlayStateRead = ord("S")
    SetColorPattern = ord("P")
    SaveColorPatterns = ord("W")
    ReadColorPattern = ord("R")
    SetLEDn = ord("l")
    ReadEEPROM = ord("e")
    WriteEEPROM = ord("E")
    GetVersion = ord("v")
    TestCommand = ord("!")
    WriteNote = ord("F")
    ReadNote = ord("f")
    Bootloader = ord("G")
    LockBootLoader = ord("L")
    SetStartupParams = ord("B")
    GetStartupParams = ord("b")
    ServerModeTickle = ord("D")
    GetChipID = ord("U")


class LEDS(IntEnum):
    """LED selection enumeration for multi-LED Blink(1) devices.

    Specifies which LED(s) to control on devices that have multiple LEDs,
    such as the Blink(1) mk2 which has both top and bottom LEDs.
    """

    All = 0
    Top = 1
    Bottom = 2


class Report(IntEnum):
    """Report type enumeration for HID communication.

    Defines the HID report numbers used for different types of
    communication with Blink(1) devices.
    """

    One = 1
    Two = 2

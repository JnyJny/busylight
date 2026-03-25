"""Kuando Busylight enumerations.

This module defines the enumerations used by Kuando Busylight devices for
ringtones and operation codes.
"""

from enum import IntEnum


class Ring(IntEnum):
    """Ringtone enumeration for Kuando Busylight devices.

    Defines the available ringtones that can be played on supported devices.
    Each ringtone has a specific numeric value that corresponds to the device's
    internal ringtone selection.
    """

    Off: int = 0
    OpenOffice: int = 136
    Quiet: int = 144
    Funky: int = 152
    FairyTale: int = 160
    KuandoTrain: int = 168
    TelephoneNordic: int = 176
    TelephoneOriginal: int = 184
    TelephonePickMeUp: int = 192
    Buzz: int = 216


class OpCode(IntEnum):
    """Operation code enumeration for Kuando Busylight commands.

    Defines the available operation codes that control device behavior.
    These codes are used in the Step command structure to specify what
    action the device should perform.
    """

    Jump: int = 0x1
    Reset: int = 0x2
    Boot: int = 0x4
    KeepAlive: int = 0x8

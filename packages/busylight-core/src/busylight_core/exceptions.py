"""Busylight Exceptions"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .hardware import Hardware
    from .light import Light


class _BaseHardwareError(Exception):
    """Base class for hardware-related errors."""

    def __init__(self, hardware: Hardware) -> None:
        self.hardware = hardware


class _BaseLightError(Exception):
    """Base class for light-related errors."""

    def __init__(self, light_subclass: type[Light]) -> None:
        self.light_subclass = light_subclass


class LightUnavailableError(_BaseLightError):
    """Previously accessible light is now not accessible."""

    def __init__(self, light: Light) -> None:
        """Initialize with the light instance that became unavailable."""
        self.light = light


class HardwareUnsupportedError(_BaseLightError):
    """The hardware supplied is not supported by this class."""

    def __init__(self, hardware: Hardware, light_subclass: type[Light]) -> None:
        """Initialize with the unsupported hardware and light class."""
        self.hardware = hardware
        self.light_subclass = light_subclass


class NoLightsFoundError(_BaseLightError):
    """No lights were discovered by this Light subclass."""


class InvalidHardwareError(_BaseHardwareError):
    """The device dictionary is missing required key/value pairs."""

    def __init__(self, device_description: dict) -> None:
        """Initialize with the invalid device description."""
        self.device_description = device_description


class HardwareAlreadyOpenError(_BaseHardwareError):
    """The hardware device is already open and cannot be opened again."""


class HardwareNotOpenError(_BaseHardwareError):
    """The hardware device is not open and cannot be used."""

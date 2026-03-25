"""USB Hardware Description

This module provides a description of USB hardware devices, including
HID and serial connections.

"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING

import serial
from loguru import logger
from serial.tools import list_ports

if TYPE_CHECKING:
    from serial.tools.list_ports_common import ListPortInfo

from . import hid
from .exceptions import InvalidHardwareError


class ConnectionType(int, Enum):
    """USB device connection protocols supported by the library.

    Defines the different communication protocols that can be used
    to interact with USB status light devices. Use these values
    with Hardware.enumerate() to filter device discovery by protocol type.
    """

    ANY: int = -1
    UNKNOWN: int = 0
    HID: int = 1
    SERIAL: int = 2
    BLUETOOTH: int = 3


HardwareHandle = hid.Device | serial.Serial


@dataclass
class Hardware:
    """Represents a USB-connected status light hardware device.

    Contains all the information needed to identify, connect to, and
    communicate with a USB device that can function as a status light.
    Hardware instances are typically created through discovery methods
    (enumerate, from_hid, from_portinfo) and then used to initialize
    Light instances for device control.
    """

    device_type: ConnectionType
    path: bytes
    vendor_id: int
    product_id: int
    serial_number: str
    manufacturer_string: str
    product_string: str | None = None
    release_number: str | None = None
    usage: int | None = None
    usage_page: int | None = None
    interface_number: int | None = None
    bus_type: int | None = None
    is_acquired: bool = False

    @classmethod
    def enumerate(cls, by_type: ConnectionType = ConnectionType.ANY) -> list[Hardware]:
        """Discover all USB devices that could potentially be status lights.

        Scans the system for USB devices using HID and serial protocols,
        creating Hardware instances for each discovered device. Use this
        for device discovery, inventory management, or when you need to
        present users with available hardware options.

        The returned Hardware instances represent raw device information
        and have not been tested for compatibility with specific Light classes.
        Use Light.claims() to determine which Light class can control each device.

        :param by_type: Limit discovery to specific connection types or scan all types
        :return: List of Hardware instances representing discovered USB devices
        :raises NotImplementedError: If the specified connection type is not supported
        """
        hardware_info = []

        match by_type:
            case ConnectionType.ANY:
                for connection_type in list(ConnectionType)[2:]:
                    with contextlib.suppress(NotImplementedError):
                        hardware_info.extend(cls.enumerate(connection_type))

            case ConnectionType.HID:
                for device_dict in hid.enumerate():
                    with contextlib.suppress(InvalidHardwareError):
                        hardware_info.append(cls.from_hid(device_dict))

            case ConnectionType.SERIAL:
                for port_info in list_ports.comports():
                    with contextlib.suppress(InvalidHardwareError):
                        hardware_info.append(cls.from_portinfo(port_info))

            case _:
                msg = f"Device connection {by_type.name} not implemented"
                raise NotImplementedError(msg)

        return hardware_info

    @classmethod
    def from_portinfo(cls, port_info: ListPortInfo) -> Hardware:
        """Create Hardware instance from serial port information.

        Converts a pyserial ListPortInfo object into a Hardware instance
        suitable for Light class initialization. Use this when you have
        serial port information from pyserial's list_ports.comports()
        and need to create a Hardware representation.

        :param port_info: Serial port information from pyserial enumeration
        :return: Hardware instance representing the serial device
        :raises InvalidHardwareError: If port information is incomplete or invalid
        """
        try:
            return cls(
                device_type=ConnectionType.SERIAL,
                vendor_id=port_info.vid,
                product_id=port_info.pid,
                path=port_info.device.encode("utf-8"),
                serial_number=port_info.serial_number,
                manufacturer_string=port_info.manufacturer,
                product_string=port_info.product,
                bus_type=1,
            )
        except Exception:
            logger.exception("%s", port_info)
            raise InvalidHardwareError(port_info.__dict__) from None

    @classmethod
    def from_hid(cls, device: dict) -> Hardware:
        """Create Hardware instance from HID device information.

        Converts a HID device dictionary (from hid.enumerate()) into a Hardware
        instance suitable for Light class initialization. Use this when you have
        HID device information and need to create a Hardware representation.

        :param device: HID device dictionary from hidapi enumeration
        :return: Hardware instance representing the HID device
        :raises InvalidHardwareError: If device information is incomplete or invalid
        """
        try:
            return cls(device_type=ConnectionType.HID, **device)
        except Exception:
            logger.exception("%s", device)
            raise InvalidHardwareError(device) from None

    @cached_property
    def device_id(self) -> tuple[int, int]:
        """A tuple of the vendor and product identifiers.

        Each item in the tuple is a 16-bit integer.
        """
        return (self.vendor_id, self.product_id)

    def __post_init__(self) -> None:
        if self.vendor_id is None:
            self.vendor_id = 0

        if self.product_id is None:
            self.product_id = 0

        if self.vendor_id:
            self.vendor_id &= 0x0FFFF

        if self.product_id:
            self.product_id &= 0x0FFFF

    def __str__(self) -> str:
        return "{vid:04x}:{pid:04x} {man} {prod} {ser} {path}".format(
            vid=self.vendor_id,
            pid=self.product_id,
            man=self.manufacturer_string,
            prod=self.product_string or "",
            ser=self.serial_number or "",
            path=self.path.decode("utf-8"),
        )

    @cached_property
    def as_dict(self) -> dict[str, int | str | bytes | None]:
        """Return hardware information as a dictionary."""
        return {
            "vendor_id": self.vendor_id,
            "product_id": self.product_id,
            "path": self.path,
            "serial_number": self.serial_number,
            "manufacturer": self.manufacturer_string,
            "product_string": self.product_string,
            "release_number": self.release_number,
            "usage": self.usage,
            "usage_page": self.usage_page,
            "bus_type": self.bus_type,
            "device_type": self.device_type.name,
        }

    @cached_property
    def handle(self) -> HardwareHandle:
        """Hardware device I/O handle."""
        handle: HardwareHandle

        match self.device_type:
            case ConnectionType.HID:
                handle = hid.Device()
            case ConnectionType.SERIAL:
                handle = serial.Serial(timeout=1)
                handle.port = self.path.decode("utf-8")
            case _:
                msg = f"Device type {self.device_type} not implemented"
                raise NotImplementedError(msg)
        return handle

    def acquire(self) -> None:
        """Open the hardware device.

        The device is available for I/O operations after this method
        returns. If the device is already acquired, no actions are
        taken.

        """
        if self.is_acquired:
            logger.debug(f"{self} already acquired")
            return

        match self.device_type:
            case ConnectionType.HID:
                self.handle.open_path(self.path)
                self.is_acquired = True
            case ConnectionType.SERIAL:
                self.handle.open()
                self.is_acquired = True
            case _:
                msg = f"{self.device_type.value.title()} hardware not implemented"
                raise NotImplementedError(msg)

    def release(self) -> None:
        """Close the hardware device.

        Subsequent I/O operations to this device will fail after this
        method returns. If the device has already been released, no
        action is taken.
        """
        if not self.is_acquired:
            logger.debug(f"{self} already released")
            return

        match self.device_type:
            case ConnectionType.HID | ConnectionType.SERIAL:
                self.handle.close()
                self.is_acquired = False
            case _:
                msg = f"{self.device_type.value.title()} hardware not implemented"
                raise NotImplementedError(msg)

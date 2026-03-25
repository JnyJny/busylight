"""Test configuration and shared fixtures."""

import pytest
from serial.tools.list_ports_common import ListPortInfo

from busylight_core.hardware import Hardware


@pytest.fixture
def serial_device_info() -> ListPortInfo:
    """Create mock serial port information for hardware testing.

    Returns a configured ListPortInfo instance with test data that
    can be used to create Hardware instances for unit testing.

    :return: Mock serial port information with test vendor/product data
    """
    info = ListPortInfo("/BOGUS/PATH")
    info.description = "Test Port"
    info.hwid = "USB VID:PID=9999:9999"
    info.manufacturer = "Test Manufacturer"
    info.product = "Test Product"
    info.vid = 0x9999
    info.pid = 0x9999
    info.serial_number = "12345678"
    return info


@pytest.fixture
def hid_device_info() -> dict:
    """Create mock HID device information for hardware testing.

    Returns a dictionary containing HID device attributes that can
    be used to create Hardware instances for unit testing.

    :return: Mock HID device data dictionary with test vendor/product info
    """
    return {
        "path": b"/BOGUS/PATH",
        "vendor_id": 0x9999,
        "product_id": 0x9999,
        "serial_number": "12345678",
        "manufacturer_string": "Test Manufacturer",
        "product_string": "Test Product",
        "usage_page": 0x01,
        "usage": 0x02,
        "interface_number": 0,
        "bus_type": 0,
    }


@pytest.fixture
def hardware_hid_device(hid_device_info: dict) -> Hardware:
    """Create mock HID Hardware instance for device testing.

    Converts mock HID device information into a Hardware instance
    that can be used in unit tests without requiring actual hardware.

    :param hid_device_info: Mock HID device data from hid_device_info fixture
    :return: Hardware instance representing a mock HID device
    """
    return Hardware.from_hid(hid_device_info)


@pytest.fixture
def hardware_serial_device(serial_device_info: ListPortInfo) -> Hardware:
    """Create mock serial Hardware instance for device testing.

    Converts mock serial port information into a Hardware instance
    that can be used in unit tests without requiring actual hardware.

    :param serial_device_info: Mock serial port data from serial_device_info fixture
    :return: Hardware instance representing a mock serial device
    """
    return Hardware.from_portinfo(serial_device_info)


@pytest.fixture
def hardware_devices(
    hardware_hid_device: Hardware, hardware_serial_device: Hardware
) -> list[Hardware]:
    """Create list of mock Hardware instances for comprehensive testing.

    Combines HID and serial mock devices into a single list for tests
    that need to verify behavior across multiple device types.

    :param hardware_hid_device: Mock HID device from hardware_hid_device fixture
    :param hardware_serial_device: Mock serial device from hardware_serial_device fixture
    :return: List containing both mock Hardware instances
    """
    return [hardware_hid_device, hardware_serial_device]

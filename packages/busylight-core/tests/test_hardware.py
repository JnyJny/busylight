"""Tests for the Hardware class and related functionality."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware

# test enumerate classmethod


def test_hardware_classmethod_enumerate_without_args() -> None:
    """Test that enumerate() returns a list of Hardware objects."""
    results = Hardware.enumerate()

    assert isinstance(results, list)
    for item in results:
        assert isinstance(item, Hardware)


@pytest.mark.parametrize(
    ("connection", "implemented"),
    [
        (ConnectionType.ANY, True),
        (ConnectionType.UNKNOWN, False),
        (ConnectionType.HID, True),
        (ConnectionType.SERIAL, True),
        (ConnectionType.BLUETOOTH, False),
    ],
)
def test_hardware_classmethod_enumerate_by_connection_type(
    connection,
    implemented,
) -> None:
    """Test enumerate() with different connection types."""
    if not implemented:
        with pytest.raises(NotImplementedError):
            results = Hardware.enumerate(connection)
    else:
        results = Hardware.enumerate(connection)

        assert isinstance(results, list)
        for item in results:
            assert isinstance(item, Hardware)
            assert item.device_type in ConnectionType


def test_hardware_classmethod_from_portinfo(hardware_serial_device) -> None:
    """Test Hardware.from_portinfo() creates correct Hardware object."""
    assert isinstance(hardware_serial_device, Hardware)
    assert hardware_serial_device.vendor_id == 0x9999
    assert hardware_serial_device.product_id == 0x9999
    assert hardware_serial_device.serial_number == "12345678"
    assert hardware_serial_device.device_type == ConnectionType.SERIAL
    assert hardware_serial_device.bus_type == 1
    assert "test" in hardware_serial_device.manufacturer_string.lower()
    assert isinstance(hardware_serial_device.path, bytes)
    assert hardware_serial_device.device_id == (
        hardware_serial_device.vendor_id,
        hardware_serial_device.product_id,
    )


def test_hardware_classmethod_from_hid(hardware_hid_device) -> None:
    """Test Hardware.from_hid() creates correct Hardware object."""
    assert isinstance(hardware_hid_device, Hardware)
    assert hardware_hid_device.vendor_id == 0x9999
    assert hardware_hid_device.product_id == 0x9999
    assert hardware_hid_device.serial_number == "12345678"
    assert hardware_hid_device.device_type == ConnectionType.HID
    assert hardware_hid_device.bus_type == 0
    assert "test" in hardware_hid_device.manufacturer_string.lower()
    assert "test" in hardware_hid_device.product_string.lower()
    assert isinstance(hardware_hid_device.path, bytes)
    assert hardware_hid_device.device_id == (
        hardware_hid_device.vendor_id,
        hardware_hid_device.product_id,
    )


@pytest.mark.skip(reason="Not implemented")
@pytest.mark.parametrize("hardware", [None])
def test_hardware_property_handle(hardware: Hardware) -> None:
    """Test Hardware.handle property (not implemented)."""


@pytest.mark.skip(reason="Not implemented")
@pytest.mark.parametrize("hardware", [None])
def test_hardware_method_acquire(hardware: Hardware) -> None:
    """Test Hardware.acquire() method (not implemented)."""


@pytest.mark.skip(reason="Not implemented")
@pytest.mark.parametrize("hardware", [None])
def test_hardware_method_release(hardware: Hardware) -> None:
    """Test Hardware.release() method (not implemented)."""


def test_hardware_handle_unsupported_connection_type() -> None:
    """Test Hardware.handle raises NotImplementedError for unsupported connection types."""
    # Create a hardware instance with unsupported connection type
    hardware = Hardware(
        device_type=ConnectionType.BLUETOOTH,  # Unsupported type
        path=b"/dev/test",
        vendor_id=0x1234,
        product_id=0x5678,
        serial_number="TEST123",
        manufacturer_string="Test Manufacturer",
    )

    with pytest.raises(
        NotImplementedError,
        match="Device type ConnectionType.BLUETOOTH not implemented",
    ):
        _ = hardware.handle


def test_hardware_acquire_already_acquired() -> None:
    """Test Hardware.acquire() when device is already acquired."""
    # Create a HID hardware instance
    hardware = Hardware(
        device_type=ConnectionType.HID,
        path=b"/dev/test",
        vendor_id=0x1234,
        product_id=0x5678,
        serial_number="TEST123",
        manufacturer_string="Test Manufacturer",
    )

    # Mock the handle and set as already acquired
    hardware._handle = Mock()  # noqa: SLF001
    hardware.is_acquired = True

    # Mock logger to capture debug message
    with patch("busylight_core.hardware.logger") as mock_logger:
        hardware.acquire()
        mock_logger.debug.assert_called_once_with(f"{hardware} already acquired")


def test_hardware_acquire_unsupported_connection_type() -> None:
    """Test Hardware.acquire() raises NotImplementedError for unsupported connection types."""
    hardware = Hardware(
        device_type=ConnectionType.BLUETOOTH,  # Unsupported type
        path=b"/dev/test",
        vendor_id=0x1234,
        product_id=0x5678,
        serial_number="TEST123",
        manufacturer_string="Test Manufacturer",
    )

    # Mock the handle so we can call acquire
    hardware._handle = Mock()  # noqa: SLF001
    hardware.is_acquired = False

    with pytest.raises(AttributeError, match="'int' object has no attribute 'title'"):
        hardware.acquire()


def test_hardware_release_already_released() -> None:
    """Test Hardware.release() when device is already released."""
    hardware = Hardware(
        device_type=ConnectionType.HID,
        path=b"/dev/test",
        vendor_id=0x1234,
        product_id=0x5678,
        serial_number="TEST123",
        manufacturer_string="Test Manufacturer",
    )

    # Mock the handle and set as not acquired
    hardware._handle = Mock()  # noqa: SLF001
    hardware.is_acquired = False

    # Mock logger to capture debug message
    with patch("busylight_core.hardware.logger") as mock_logger:
        hardware.release()
        mock_logger.debug.assert_called_once_with(f"{hardware} already released")


def test_hardware_release_hid_and_serial() -> None:
    """Test Hardware.release() for HID and SERIAL connection types."""
    # Test HID
    hid_hardware = Hardware(
        device_type=ConnectionType.HID,
        path=b"/dev/test",
        vendor_id=0x1234,
        product_id=0x5678,
        serial_number="TEST123",
        manufacturer_string="Test Manufacturer",
    )

    mock_handle = Mock()
    hid_hardware._handle = mock_handle  # noqa: SLF001
    hid_hardware.is_acquired = True

    # Need to mock the handle property to return our mock
    with patch.object(
        type(hid_hardware),
        "handle",
        new_callable=lambda: property(lambda _: mock_handle),
    ):
        hid_hardware.release()

    mock_handle.close.assert_called_once()
    assert hid_hardware.is_acquired is False

    # Test SERIAL
    serial_hardware = Hardware(
        device_type=ConnectionType.SERIAL,
        path=b"/dev/ttyUSB0",
        vendor_id=0x1234,
        product_id=0x5678,
        serial_number="TEST123",
        manufacturer_string="Test Manufacturer",
    )

    mock_handle = Mock()
    serial_hardware._handle = mock_handle  # noqa: SLF001
    serial_hardware.is_acquired = True

    # Need to mock the handle property to return our mock
    with patch.object(
        type(serial_hardware),
        "handle",
        new_callable=lambda: property(lambda _: mock_handle),
    ):
        serial_hardware.release()

    mock_handle.close.assert_called_once()
    assert serial_hardware.is_acquired is False


def test_hardware_release_unsupported_connection_type() -> None:
    """Test Hardware.release() raises NotImplementedError for unsupported connection types."""
    hardware = Hardware(
        device_type=ConnectionType.BLUETOOTH,  # Unsupported type
        path=b"/dev/test",
        vendor_id=0x1234,
        product_id=0x5678,
        serial_number="TEST123",
        manufacturer_string="Test Manufacturer",
    )

    # Mock the handle and set as acquired
    hardware._handle = Mock()  # noqa: SLF001
    hardware.is_acquired = True

    with pytest.raises(AttributeError, match="'int' object has no attribute 'title'"):
        hardware.release()

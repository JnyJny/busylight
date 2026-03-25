"""Tests for the hid module compatibility layer."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.exceptions import HardwareAlreadyOpenError, HardwareNotOpenError
from busylight_core.hid import Device
from busylight_core.hid import enumerate as hid_enumerate


class TestEnumerate:
    """Tests for the enumerate function."""

    def test_enumerate_returns_list_of_dicts(self) -> None:
        """Test that enumerate returns a list of dictionaries."""
        mock_device_info = [
            {"vendor_id": 0x1234, "product_id": 0x5678, "path": b"/dev/hidraw0"},
            {"vendor_id": 0x9999, "product_id": 0x8888, "path": b"/dev/hidraw1"},
        ]

        with patch("busylight_core.hid.hid.enumerate", return_value=mock_device_info):
            result = hid_enumerate()

        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            assert isinstance(item, dict)
            assert "vendor_id" in item
            assert "product_id" in item
            assert "path" in item

    def test_enumerate_empty_list(self) -> None:
        """Test enumerate with no devices."""
        with patch("busylight_core.hid.hid.enumerate", return_value=[]):
            result = hid_enumerate()

        assert result == []


class TestDeviceInitialization:
    """Tests for Device initialization and library detection."""

    def test_device_init_with_cython_hidapi(self) -> None:
        """Test Device initialization with cython-hidapi (hid.device available)."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()

        assert device.handle is mock_device
        assert device.is_open is False

    def test_device_init_with_pyhidapi_fallback(self) -> None:
        """Test Device initialization with pyhidapi fallback."""
        with patch("busylight_core.hid.hid.device", side_effect=AttributeError):
            device = Device()

        assert device.handle is None
        assert device.is_open is False

    def test_is_open_property(self) -> None:
        """Test the is_open property."""
        with patch("busylight_core.hid.hid.device", return_value=Mock()):
            device = Device()

        assert device.is_open is False
        with pytest.raises(AttributeError):
            device.is_open = True


class TestDeviceErrorHandling:
    """Tests for Device error handling."""

    def test_error_property_normal_case(self) -> None:
        """Test error property returns error from handle."""
        mock_device = Mock()
        mock_device.error.return_value = "Test error message"

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()

        assert device.error == "Test error message"
        mock_device.error.assert_called_once()

    def test_error_property_ioerror_case(self) -> None:
        """Test error property handles IOError exception."""
        mock_device = Mock()
        mock_device.error.side_effect = OSError("Device not found")

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()

        assert device.error == "Device not found"


class TestDeviceOpen:
    """Tests for Device.open method."""

    def test_open_with_cython_hidapi(self) -> None:
        """Test opening device with cython-hidapi."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device.open(0x1234, 0x5678)

        mock_device.open.assert_called_once_with(0x1234, 0x5678, None)
        assert device.is_open

    def test_open_with_cython_hidapi_and_serial(self) -> None:
        """Test opening device with cython-hidapi and serial number."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device.open(0x1234, 0x5678, "SERIAL123")

        mock_device.open.assert_called_once_with(0x1234, 0x5678, "SERIAL123")
        assert device.is_open

    def test_open_with_pyhidapi_fallback(self) -> None:
        """Test opening device with pyhidapi fallback."""
        mock_hid_device = Mock()

        with (
            patch("busylight_core.hid.hid.device", side_effect=AttributeError),
            patch(
                "busylight_core.hid.hid.Device",
                return_value=mock_hid_device,
                create=True,
            ) as mock_device_class,
        ):
            device = Device()
            device.open(0x1234, 0x5678)

        # Check that hid.Device was called with correct parameters
        mock_device_class.assert_called_once_with(vid=0x1234, pid=0x5678, serial=None)
        assert device.handle is mock_hid_device
        assert device.is_open

    def test_open_with_pyhidapi_fallback_and_serial(self) -> None:
        """Test opening device with pyhidapi fallback and serial number."""
        mock_hid_device = Mock()

        with (
            patch("busylight_core.hid.hid.device", side_effect=AttributeError),
            patch(
                "busylight_core.hid.hid.Device",
                return_value=mock_hid_device,
                create=True,
            ) as mock_device_class,
        ):
            device = Device()
            device.open(0x1234, 0x5678, "SERIAL123")

        mock_device_class.assert_called_once_with(
            vid=0x1234, pid=0x5678, serial="SERIAL123"
        )
        assert device.handle is mock_hid_device
        assert device.is_open

    def test_open_already_open_device(self) -> None:
        """Test opening an already open device raises HardwareAlreadyOpenError."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = True  # noqa: SLF001

            with pytest.raises(HardwareAlreadyOpenError):
                device.open(0x1234, 0x5678)


class TestDeviceOpenPath:
    """Tests for Device.open_path method."""

    def test_open_path_with_bytes(self) -> None:
        """Test opening device by path with bytes."""
        mock_device = Mock()
        test_path = b"/dev/hidraw0"

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device.open_path(test_path)

        mock_device.open_path.assert_called_once_with(test_path)
        assert device.is_open

    def test_open_path_with_string(self) -> None:
        """Test opening device by path with string (converted to bytes)."""
        mock_device = Mock()
        test_path = "/dev/hidraw0"

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device.open_path(test_path)

        mock_device.open_path.assert_called_once_with(test_path.encode("utf-8"))
        assert device.is_open

    def test_open_path_with_pyhidapi_fallback(self) -> None:
        """Test opening device by path with pyhidapi fallback."""
        mock_hid_device = Mock()
        test_path = b"/dev/hidraw0"

        with (
            patch("busylight_core.hid.hid.device", side_effect=AttributeError),
            patch(
                "busylight_core.hid.hid.Device",
                return_value=mock_hid_device,
                create=True,
            ) as mock_device_class,
        ):
            device = Device()
            device.open_path(test_path)

        mock_device_class.assert_called_once_with(path=test_path)
        assert device.handle is mock_hid_device
        assert device.is_open

    def test_open_path_already_open_device(self) -> None:
        """Test opening path on already open device raises HardwareAlreadyOpenError."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = True  # noqa: SLF001

            with pytest.raises(HardwareAlreadyOpenError):
                device.open_path(b"/dev/hidraw0")


class TestDeviceClose:
    """Tests for Device.close method."""

    def test_close_open_device(self) -> None:
        """Test closing an open device."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = True  # noqa: SLF001
            device.close()

        mock_device.close.assert_called_once()
        assert device.is_open is False

    def test_close_not_open_device(self) -> None:
        """Test closing a device that's not open raises IOError."""
        mock_device = Mock()
        mock_device.close.side_effect = AttributeError("close")

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = True  # noqa: SLF001

            with pytest.raises(HardwareNotOpenError):
                device.close()


class TestDeviceOperations:
    """Tests for Device I/O operations."""

    def test_read_open_device(self) -> None:
        """Test reading from an open device."""
        mock_device = Mock()
        mock_device.read.return_value = [0x01, 0x02, 0x03]

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = True  # noqa: SLF001

            result = device.read(3)

        mock_device.read.assert_called_once_with(3, None)
        assert result == [0x01, 0x02, 0x03]

    def test_read_with_timeout(self) -> None:
        """Test reading from device with timeout."""
        mock_device = Mock()
        mock_device.read.return_value = [0x01, 0x02, 0x03]

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = True  # noqa: SLF001

            result = device.read(3, 1000)

        mock_device.read.assert_called_once_with(3, 1000)
        assert result == [0x01, 0x02, 0x03]

    def test_read_closed_device(self) -> None:
        """Test reading from a closed device raises HardwareNotOpenError."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = False  # noqa: SLF001

            with pytest.raises(HardwareNotOpenError):
                device.read(3)

    def test_write_open_device(self) -> None:
        """Test writing to an open device."""
        mock_device = Mock()
        mock_device.write.return_value = 3
        test_data = b"\x01\x02\x03"

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = True  # noqa: SLF001

            result = device.write(test_data)

        mock_device.write.assert_called_once_with(test_data)
        assert result == 3

    def test_write_closed_device(self) -> None:
        """Test writing to a closed device raises HardwareNotOpenError."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = False  # noqa: SLF001

            with pytest.raises(HardwareNotOpenError):
                device.write(b"\x01\x02\x03")

    def test_get_feature_report_open_device(self) -> None:
        """Test getting feature report from an open device."""
        mock_device = Mock()
        mock_device.get_feature_report.return_value = [0x01, 0x02, 0x03]

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = True  # noqa: SLF001

            result = device.get_feature_report(1, 3)

        mock_device.get_feature_report.assert_called_once_with(1, 3)
        assert result == [0x01, 0x02, 0x03]

    def test_get_feature_report_closed_device(self) -> None:
        """Test getting feature report from a closed device raises HardwareNotOpenError."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = False  # noqa: SLF001

            with pytest.raises(HardwareNotOpenError):
                device.get_feature_report(1, 3)

    def test_send_feature_report_open_device(self) -> None:
        """Test sending feature report to an open device."""
        mock_device = Mock()
        mock_device.send_feature_report.return_value = 3
        test_data = b"\x01\x02\x03"

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = True  # noqa: SLF001

            result = device.send_feature_report(test_data)

        mock_device.send_feature_report.assert_called_once_with(test_data)
        assert result == 3

    def test_send_feature_report_closed_device(self) -> None:
        """Test sending feature report to a closed device raises HardwareNotOpenError."""
        mock_device = Mock()

        with patch("busylight_core.hid.hid.device", return_value=mock_device):
            device = Device()
            device._is_open = False  # noqa: SLF001

            with pytest.raises(HardwareNotOpenError):
                device.send_feature_report(b"\x01\x02\x03")

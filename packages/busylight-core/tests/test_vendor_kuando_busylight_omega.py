"""Tests for Kuando Busylight Omega device-specific functionality."""

from unittest.mock import Mock

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.kuando import BusylightOmega


class TestKuandoBusylightOmega:
    """Test the Busylight Omega device-specific functionality."""

    @pytest.fixture
    def mock_hardware(self) -> Hardware:
        """Create mock hardware for testing Omega-specific device IDs."""
        hardware = Mock(spec=Hardware)
        hardware.vendor_id = 0x27BB
        hardware.product_id = 0x3BCD
        hardware.device_id = (0x27BB, 0x3BCD)
        hardware.connection_type = ConnectionType.HID
        hardware.acquire = Mock()
        hardware.release = Mock()
        return hardware

    @pytest.fixture
    def busylight(self, mock_hardware) -> BusylightOmega:
        """Create a BusylightOmega instance for testing."""
        # Mock the hardware handle methods
        mock_hardware.handle = Mock()
        mock_hardware.handle.write = Mock(return_value=64)
        mock_hardware.handle.read = Mock(return_value=b"\x00" * 64)

        return BusylightOmega(mock_hardware, reset=False, exclusive=False)

    def test_supported_device_ids(self) -> None:
        """Test Omega supported_device_ids contains expected devices."""
        device_ids = BusylightOmega.supported_device_ids
        assert (0x27BB, 0x3BCD) in device_ids
        assert (0x27BB, 0x3BCF) in device_ids
        assert all("Busylight Omega" in name for name in device_ids.values())
        # Ensure these are Omega-specific and not Alpha IDs
        assert (0x04D8, 0xF848) not in device_ids  # Alpha ID
        assert (0x27BB, 0x3BCA) not in device_ids  # Alpha ID

    def test_vendor_method(self, busylight) -> None:
        """Test vendor() method returns correct vendor name."""
        assert busylight.vendor() == "Kuando"

    def test_claims_method_with_omega_hardware(self, mock_hardware) -> None:
        """Test claims() method with Omega-specific hardware."""
        # Test with Omega device ID
        mock_hardware.device_id = (0x27BB, 0x3BCD)
        assert BusylightOmega.claims(mock_hardware) is True

        # Test with another Omega device ID
        mock_hardware.device_id = (0x27BB, 0x3BCF)
        assert BusylightOmega.claims(mock_hardware) is True

        # Test with Alpha device ID (should not claim)
        mock_hardware.device_id = (0x04D8, 0xF848)
        assert BusylightOmega.claims(mock_hardware) is False

        # Test with another Alpha device ID (should not claim)
        mock_hardware.device_id = (0x27BB, 0x3BCA)
        assert BusylightOmega.claims(mock_hardware) is False

        # Test with unknown device ID
        mock_hardware.device_id = (0x1234, 0x5678)
        assert BusylightOmega.claims(mock_hardware) is False

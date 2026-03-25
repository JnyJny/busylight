"""Comprehensive tests for the Light base class to improve coverage."""

from typing import ClassVar
from unittest.mock import Mock, patch

import pytest

from busylight_core.exceptions import HardwareUnsupportedError, LightUnavailableError
from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.light import Light
from busylight_core.mixins import ColorableMixin


class MockLightSubclass(ColorableMixin, Light):
    """Mock Light subclass for testing."""

    supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
        (0x1234, 0x5678): "MockLight"
    }

    def __bytes__(self) -> bytes:
        return b"\x01\x02\x03\x04"

    def _on(self, color: tuple[int, int, int], led: int = 0) -> None:
        """Turn the light on with the specified color (mock)."""


def create_mock_hardware(
    vendor_id=0x1234, product_id=0x5678, path=b"/dev/hidraw0"
) -> Hardware:
    """Create a mock hardware device."""
    mock_hardware = Mock(spec=Hardware)
    mock_hardware.device_id = (vendor_id, product_id)
    mock_hardware.device_type = ConnectionType.HID
    mock_hardware.path = path
    mock_hardware.product_string = "MockLight"
    mock_hardware.vendor_id = vendor_id
    mock_hardware.product_id = product_id
    mock_hardware.handle = Mock()
    mock_hardware.handle.read = Mock(return_value=b"\x00\x01\x02\x03")
    mock_hardware.handle.write = Mock()
    mock_hardware.acquire = Mock()
    mock_hardware.release = Mock()
    return mock_hardware


class TestLightFirstLight:
    """Test first_light method coverage."""

    def test_first_light_with_exception_handling(self) -> None:
        """Test first_light when subclass init raises exception."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(MockLightSubclass, "available_hardware") as mock_available,
            patch.object(
                MockLightSubclass,
                "__init__",
                side_effect=Exception("Device initialization failed"),
            ),
        ):
            mock_available.return_value = {MockLightSubclass: [mock_hardware]}

            with pytest.raises(Exception, match="Device initialization failed"):
                MockLightSubclass.first_light()


class TestLightRepr:
    """Test __repr__ method coverage."""

    def test_repr_method(self) -> None:
        """Test __repr__ method - covers line 142."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware, reset=True, exclusive=True)

            repr_str = repr(light)

            assert "MockLightSubclass(" in repr_str
            assert "reset=True" in repr_str
            assert "exclusive=True" in repr_str


class TestLightPath:
    """Test path property coverage."""

    def test_path_property_cached(self) -> None:
        """Test path property decode - covers line 153."""
        mock_hardware = create_mock_hardware(path=b"/dev/hidraw1")

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            path = light.path
            assert path == "/dev/hidraw1"

            # Test caching
            path2 = light.path
            assert path2 == "/dev/hidraw1"
            assert path is path2


class TestLightPlatform:
    """Test platform property coverage."""

    def test_platform_property_windows(self) -> None:
        """Test platform property for Windows - covers line 160."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
            patch("busylight_core.light.platform.system", return_value="Windows"),
            patch("busylight_core.light.platform.release", return_value="10"),
        ):
            light = MockLightSubclass(mock_hardware)
            platform = light.platform

            assert platform == "Windows_10"


class TestLightSortKey:
    """Test sort_key property coverage."""

    def test_sort_key_property(self) -> None:
        """Test sort_key property - covers line 166."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
            patch.object(MockLightSubclass, "vendor", return_value="TestVendor"),
        ):
            light = MockLightSubclass(mock_hardware)

            assert isinstance(light.sort_key, tuple)
            assert len(light.sort_key) == 3
            assert light.sort_key[0] == "testvendor"
            assert light.sort_key[1] == "mocklight"
            assert light.sort_key[2] == "/dev/hidraw0"


class TestLightEquality:
    """Test __eq__ method coverage."""

    def test_eq_method_attribute_error(self) -> None:
        """Test __eq__ method when other object lacks sort_key."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            # Test with object that doesn't have sort_key
            class NoSortKeyObject:
                pass

            other = NoSortKeyObject()

            with pytest.raises(TypeError):
                assert light == other


class TestLightComparison:
    """Test __lt__ method coverage."""

    def test_lt_method_not_light_instance(self) -> None:
        """Test __lt__ method with non-Light instance - covers lines 176-177."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            # Test the actual __lt__ method directly to get NotImplemented
            result = light.__lt__("not a light")
            assert result is NotImplemented

    def test_lt_method_comparison_logic(self) -> None:
        """Test __lt__ method comparison logic - covers lines 179-183."""
        mock_hardware1 = create_mock_hardware(path=b"/dev/hidraw0")
        mock_hardware2 = create_mock_hardware(path=b"/dev/hidraw1")

        with (
            patch.object(mock_hardware1, "acquire"),
            patch.object(mock_hardware2, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light1 = MockLightSubclass(mock_hardware1)
            light2 = MockLightSubclass(mock_hardware2)

            # Test comparison - should compare based on sort_key
            result = light1 < light2
            assert isinstance(result, bool)

    def test_lt_method_equal_sort_keys(self) -> None:
        """Test __lt__ method when sort keys are equal - covers line 183."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light1 = MockLightSubclass(mock_hardware)
            light2 = MockLightSubclass(mock_hardware)

            # Mock same sort keys
            sort_key = ("vendor", "name", "/dev/hidraw0")
            light1.sort_key = sort_key
            light2.sort_key = sort_key

            result = light1 < light2
            assert result is False


class TestLightHash:
    """Test __hash__ method coverage."""

    def test_hash_method_caching(self) -> None:
        """Test __hash__ method caching - covers lines 186-191."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            # First call should compute hash
            hash1 = hash(light)
            assert isinstance(hash1, int)

            # Second call should use cached value
            hash2 = hash(light)
            assert hash1 == hash2


class TestLightHex:
    """Test hex property coverage."""

    def test_hex_property(self) -> None:
        """Test hex property - covers line 201."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            hex_str = light.hex
            assert isinstance(hex_str, str)
            assert hex_str == "01:02:03:04"  # From MockLightSubclass.__bytes__


class TestLightReadStrategy:
    """Test read_strategy property coverage."""

    def test_read_strategy_property(self) -> None:
        """Test read_strategy property - covers line 206."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            read_strategy = light.read_strategy
            assert read_strategy is mock_hardware.handle.read


class TestLightExclusiveAccess:
    """Test exclusive_access context manager coverage."""

    def test_exclusive_access_non_exclusive_mode(self) -> None:
        """Test exclusive_access when not in exclusive mode - covers lines 222, 227."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            # Create light in non-exclusive mode
            light = MockLightSubclass(mock_hardware, exclusive=False)

            with light.exclusive_access():
                # Should acquire inside context
                mock_hardware.acquire.assert_called()

            # Should release after context
            mock_hardware.release.assert_called()


class TestLightUpdate:
    """Test update method coverage."""

    def test_update_windows_10_platform(self) -> None:
        """Test update method with Windows 10 platform - covers line 236."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            # Mock platform to be Windows_10
            light.platform = "Windows_10"

            with patch.object(light, "exclusive_access"):
                light.update()

                # Should have called write_strategy with prepended zero byte
                expected_data = bytes([0]) + b"\x01\x02\x03\x04"
                mock_hardware.handle.write.assert_called_once_with(expected_data)

    def test_update_unsupported_platform(self) -> None:
        """Test update method with unsupported platform - covers lines 239-240."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            # Mock platform to be unsupported
            light.platform = "UnsupportedOS_1.0"

            with (
                patch.object(light, "exclusive_access"),
                patch("busylight_core.light.logger.info") as mock_logger,
            ):
                light.update()

                # Should log unsupported OS message
                mock_logger.assert_called_once_with(
                    "Unsupported OS UnsupportedOS_1.0, hoping for the best."
                )

    def test_update_write_strategy_exception(self) -> None:
        """Test update method when write_strategy raises exception."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            # Mock write_strategy to raise exception
            mock_hardware.handle.write.side_effect = Exception("Write failed")

            with (
                patch.object(light, "exclusive_access"),
                patch("busylight_core.light.logger.error") as mock_logger,
            ):
                with pytest.raises(LightUnavailableError):
                    light.update()

                # Should log error
                mock_logger.assert_called_once()


class TestLightIntegration:
    """Integration tests for Light class."""

    def test_complete_light_workflow(self) -> None:
        """Test a complete workflow with Light class."""
        mock_hardware = create_mock_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light = MockLightSubclass(mock_hardware)

            # Test various properties and methods
            assert light.name == "MockLight"
            assert (
                light.vendor() == "Tests"
            )  # From module path (tests.test_light_comprehensive)
            assert isinstance(light.path, str)
            assert isinstance(light.platform, str)
            assert isinstance(light.hex, str)
            assert callable(light.read_strategy)
            assert callable(light.write_strategy)

            # Test context manager
            with light.exclusive_access():
                pass

            # Test update
            light.update()

            # Test batch_update
            with light.batch_update():
                light.color = (255, 0, 0)

            # Test on/off
            light.on((0, 255, 0))
            light.off()

            # Test reset
            light.reset()


class TestLightEdgeCases:
    """Test edge cases and error conditions."""

    def test_unsupported_hardware_initialization(self) -> None:
        """Test Light initialization with unsupported hardware."""
        # Create hardware that won't be claimed by MockLightSubclass
        mock_hardware = create_mock_hardware(vendor_id=0x9999, product_id=0x9999)

        with pytest.raises(HardwareUnsupportedError):
            MockLightSubclass(mock_hardware)

    def test_light_comparison_edge_cases(self) -> None:
        """Test light comparison edge cases."""
        mock_hardware1 = create_mock_hardware()
        mock_hardware2 = create_mock_hardware()

        with (
            patch.object(mock_hardware1, "acquire"),
            patch.object(mock_hardware2, "acquire"),
            patch.object(MockLightSubclass, "reset"),
        ):
            light1 = MockLightSubclass(mock_hardware1)
            light2 = MockLightSubclass(mock_hardware2)

            assert light1 == light2

            # Test hash consistency
            hash1 = hash(light1)
            hash2 = hash(light1)
            assert hash1 == hash2

            # Test sorting
            lights = [light1, light2]
            sorted_lights = sorted(lights)
            assert len(sorted_lights) == 2
            assert sorted_lights == lights


class TestLightUdevRules:
    """Test udev_rules classmethod."""

    def test_udev_rules_with_supported_device_ids(self) -> None:
        """Test udev_rules method with a concrete subclass that has supported_device_ids."""
        # Use MockLightSubclass which has supported_device_ids
        rules = MockLightSubclass.udev_rules()

        # Should return a dictionary with device ID as key
        assert isinstance(rules, dict)
        assert (0x1234, 0x5678) in rules

        rule_list = rules[(0x1234, 0x5678)]
        assert isinstance(rule_list, list)
        assert len(rule_list) == 3  # Comment + 2 rule formats

        # Check comment line
        assert rule_list[0] == "# Tests MockLightSubclass udev rules"

        # Check USB subsystem rule
        expected_usb = 'SUBSYSTEMS=="usb", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="5678", MODE="0666"'
        assert rule_list[1] == expected_usb

        # Check hidraw rule
        expected_hidraw = 'KERNEL=="hidraw*", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="5678", MODE="0666"'
        assert rule_list[2] == expected_hidraw

    def test_udev_rules_with_custom_mode(self) -> None:
        """Test udev_rules method with custom file mode."""
        rules = MockLightSubclass.udev_rules(mode=0o664)

        rule_list = rules[(0x1234, 0x5678)]

        # Check that custom mode is applied
        expected_usb = 'SUBSYSTEMS=="usb", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="5678", MODE="0664"'
        assert rule_list[1] == expected_usb

        expected_hidraw = 'KERNEL=="hidraw*", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="5678", MODE="0664"'
        assert rule_list[2] == expected_hidraw

    def test_udev_rules_with_multiple_device_ids(self) -> None:
        """Test udev_rules method with multiple device IDs."""

        class MultiDeviceMockLight(ColorableMixin, Light):
            """Mock Light with multiple device IDs."""

            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
                (0x1234, 0x5678): "Device1",
                (0xABCD, 0xEF01): "Device2",
                (0x0001, 0x0002): "Device3",
            }

            def __bytes__(self) -> bytes:
                return b"\x01\x02\x03\x04"

            def on(self, color: tuple[int, int, int], led: int = 0) -> None:
                pass

        rules = MultiDeviceMockLight.udev_rules()

        # Should have rules for all device IDs
        assert len(rules) == 3
        assert (0x1234, 0x5678) in rules
        assert (0xABCD, 0xEF01) in rules
        assert (0x0001, 0x0002) in rules

        # Check that each device has correct vendor/product IDs
        rule_list_1 = rules[(0x1234, 0x5678)]
        assert 'ATTRS{idVendor}=="1234"' in rule_list_1[1]
        assert 'ATTRS{idProduct}=="5678"' in rule_list_1[1]

        rule_list_2 = rules[(0xABCD, 0xEF01)]
        assert 'ATTRS{idVendor}=="abcd"' in rule_list_2[1]
        assert 'ATTRS{idProduct}=="ef01"' in rule_list_2[1]

    def test_udev_rules_with_no_supported_device_ids(self) -> None:
        """Test udev_rules method with abstract base class (no supported_device_ids)."""

        class AbstractMockLight(Light):
            """Mock Light with no supported_device_ids (abstract)."""

            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {}

            def __bytes__(self) -> bytes:
                return b"\x01\x02\x03\x04"

            def on(self, color: tuple[int, int, int], led: int = 0) -> None:
                pass

        class ConcreteMockLight1(ColorableMixin, AbstractMockLight):
            """Concrete implementation 1."""

            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
                (0x1111, 0x2222): "Concrete1"
            }

        class ConcreteMockLight2(ColorableMixin, AbstractMockLight):
            """Concrete implementation 2."""

            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
                (0x3333, 0x4444): "Concrete2"
            }

        with patch.object(
            AbstractMockLight,
            "subclasses",
            return_value=[ConcreteMockLight1, ConcreteMockLight2],
        ):
            rules = AbstractMockLight.udev_rules()

        # Should aggregate rules from all subclasses
        assert len(rules) == 2
        assert (0x1111, 0x2222) in rules
        assert (0x3333, 0x4444) in rules

    def test_udev_rules_duplicate_device_ids_first_wins(self) -> None:
        """Test that when duplicate device IDs exist, first one wins."""

        class DuplicateDeviceMockLight1(ColorableMixin, Light):
            """First mock light with shared device ID."""

            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
                (0x1234, 0x5678): "FirstDevice"
            }

            def __bytes__(self) -> bytes:
                return b"\x01"

            def on(self, color: tuple[int, int, int], led: int = 0) -> None:
                pass

        class DuplicateDeviceMockLight2(ColorableMixin, Light):
            """Second mock light with same device ID."""

            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
                (0x1234, 0x5678): "SecondDevice"
            }

            def __bytes__(self) -> bytes:
                return b"\x02"

            def on(self, color: tuple[int, int, int], led: int = 0) -> None:
                pass

        class AbstractDuplicateLight(Light):
            """Abstract class to test duplicate handling."""

            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {}

            def __bytes__(self) -> bytes:
                return b"\x00"

            def on(self, color: tuple[int, int, int], led: int = 0) -> None:
                pass

        # Mock subclasses method to return duplicates
        with patch.object(
            AbstractDuplicateLight,
            "subclasses",
            return_value=[DuplicateDeviceMockLight1, DuplicateDeviceMockLight2],
        ):
            rules = AbstractDuplicateLight.udev_rules()

        # Should only have one entry for the duplicate device ID
        assert len(rules) == 1
        assert (0x1234, 0x5678) in rules

        # Should be from the first subclass
        rule_list = rules[(0x1234, 0x5678)]
        assert "DuplicateDeviceMockLight1" in rule_list[0]

    def test_udev_rules_vendor_method_called(self) -> None:
        """Test that vendor() method is called for comment generation."""

        class VendorMockLight(ColorableMixin, Light):
            """Mock Light to test vendor method usage."""

            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
                (0x1234, 0x5678): "TestDevice"
            }

            @staticmethod
            def vendor() -> str:
                return "TestVendor"

            def __bytes__(self) -> bytes:
                return b"\x01"

            def on(self, color: tuple[int, int, int], led: int = 0) -> None:
                pass

        rules = VendorMockLight.udev_rules()
        rule_list = rules[(0x1234, 0x5678)]

        # Check that vendor name appears in comment
        assert rule_list[0] == "# TestVendor VendorMockLight udev rules"

    def test_udev_rules_hexadecimal_formatting(self) -> None:
        """Test that vendor and product IDs are correctly formatted as hex."""

        class HexTestMockLight(ColorableMixin, Light):
            """Mock Light to test hex formatting."""

            supported_device_ids: ClassVar[dict[tuple[int, int], str]] = {
                (0x001, 0x002): "LowNumbers",  # Should be padded to 4 digits
                (0xFFFF, 0xABCD): "HighNumbers",  # Should be lowercase
            }

            def __bytes__(self) -> bytes:
                return b"\x01"

            def on(self, color: tuple[int, int, int], led: int = 0) -> None:
                pass

        rules = HexTestMockLight.udev_rules()

        # Check low numbers are padded
        low_rules = rules[(0x001, 0x002)]
        assert 'ATTRS{idVendor}=="0001"' in low_rules[1]
        assert 'ATTRS{idProduct}=="0002"' in low_rules[1]

        # Check high numbers are lowercase
        high_rules = rules[(0xFFFF, 0xABCD)]
        assert 'ATTRS{idVendor}=="ffff"' in high_rules[1]
        assert 'ATTRS{idProduct}=="abcd"' in high_rules[1]

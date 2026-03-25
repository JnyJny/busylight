"""Tests for the Luxafor Mute device."""

from unittest.mock import Mock, patch

import pytest

from busylight_core.hardware import ConnectionType, Hardware
from busylight_core.vendors.luxafor.flag import Flag
from busylight_core.vendors.luxafor.mute import Mute


def create_mock_mute_hardware() -> Hardware:
    """Create a properly configured mock hardware for Mute device."""
    mock_hardware = Mock(spec=Hardware)
    mock_hardware.device_id = (0x4D8, 0xF372)
    mock_hardware.device_type = ConnectionType.HID
    mock_hardware.path = b"/dev/hidraw0"
    mock_hardware.product_string = "Luxafor Mute"
    mock_hardware.vendor_id = 0x4D8
    mock_hardware.product_id = 0xF372
    return mock_hardware


class TestLuxaforMute:
    """Test cases for Luxafor Mute device implementation."""

    def test_supported_device_ids(self) -> None:
        """Test that supported_device_ids contains correct device mapping."""
        assert isinstance(Mute.supported_device_ids, dict)
        assert (0x4D8, 0xF372) in Mute.supported_device_ids
        assert Mute.supported_device_ids[(0x4D8, 0xF372)] == "Mute"

    def test_is_button_property(self) -> None:
        """Test that is_button property returns True for Mute device."""
        mock_hardware = create_mock_mute_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Mute, "reset"):
            mute = Mute(mock_hardware)
            assert mute.is_button is True

    def test_button_on_response_66_sets_button_false(self) -> None:
        """Test button_on when device response[0] == 66 sets _button to False."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(
                Mute, "read_strategy", return_value=[66, 0, 0, 0, 0, 0, 0, 0]
            ) as mock_read,
        ):
            mute = Mute(mock_hardware)
            result = mute.button_on
            mock_read.assert_called_once_with(8, 200)
            assert result is False  # Returns False after processing

    def test_button_on_response_131_true(self) -> None:
        """Test button_on when device response[0] == 131 and results[1] is truthy."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(
                Mute, "read_strategy", return_value=[131, 1, 0, 0, 0, 0, 0, 0]
            ) as mock_read,
        ):
            mute = Mute(mock_hardware)
            result = mute.button_on

            mock_read.assert_called_once_with(8, 200)
            assert result is True

    def test_button_on_response_131_false(self) -> None:
        """Test button_on when device response[0] == 131 and results[1] is falsy."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(
                Mute, "read_strategy", return_value=[131, 0, 0, 0, 0, 0, 0, 0]
            ) as mock_read,
        ):
            mute = Mute(mock_hardware)
            result = mute.button_on

            mock_read.assert_called_once_with(8, 200)
            assert result is False

    def test_button_on_response_131_with_nonzero_value(self) -> None:
        """Test button_on when device response[0] == 131 and results[1] != 0."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(
                Mute, "read_strategy", return_value=[131, 255, 0, 0, 0, 0, 0, 0]
            ) as mock_read,
        ):
            mute = Mute(mock_hardware)
            result = mute.button_on

            mock_read.assert_called_once_with(8, 200)
            assert result is True

    def test_button_on_index_error_handling(self) -> None:
        """Test button_on handles IndexError gracefully and returns False."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(Mute, "read_strategy", return_value=[]) as mock_read,
        ):
            mute = Mute(mock_hardware)
            result = mute.button_on

            mock_read.assert_called_once_with(8, 200)
            assert result is False

    def test_button_on_index_error_with_short_response(self) -> None:
        """Test button_on handles IndexError when response is too short."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(Mute, "read_strategy", return_value=[131]) as mock_read,
        ):  # Missing results[1]
            mute = Mute(mock_hardware)
            result = mute.button_on

            mock_read.assert_called_once_with(8, 200)
            assert result is False

    def test_button_on_unknown_response_code(self) -> None:
        """Test button_on with unknown response code returns False."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(
                Mute, "read_strategy", return_value=[99, 1, 0, 0, 0, 0, 0, 0]
            ) as mock_read,
        ):
            mute = Mute(mock_hardware)
            result = mute.button_on

            mock_read.assert_called_once_with(8, 200)
            assert result is False


class TestLuxaforMuteInheritance:
    """Test inheritance and integration aspects of Luxafor Mute."""

    def test_inherits_from_flag(self) -> None:
        """Test that Mute properly inherits from Flag class."""
        assert issubclass(Mute, Flag)

        # Test that Mute has all the Flag methods
        mute_methods = dir(Mute)
        dir(Flag)

        # Key Flag methods should be available in Mute
        expected_methods = ["claims", "state", "__bytes__", "supported_device_ids"]
        for method in expected_methods:
            assert method in mute_methods

    def test_device_claiming_logic(self) -> None:
        """Test that Mute can properly claim devices using inherited logic."""
        mock_hardware = create_mock_mute_hardware()

        result = Mute.claims(mock_hardware)
        assert result is True

    def test_device_claiming_wrong_device(self) -> None:
        """Test that Mute rejects devices it doesn't support."""
        # Create a mock hardware that should NOT be claimed by Mute
        mock_hardware = Mock(spec=Hardware)
        mock_hardware.vendor_id = 0x1234
        mock_hardware.product_id = 0x5678
        mock_hardware.device_id = (0x1234, 0x5678)
        mock_hardware.product_string = "Other Device"

        result = Mute.claims(mock_hardware)
        assert result is False

    def test_bytes_conversion_inheritance(self) -> None:
        """Test that __bytes__ method works through inheritance."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(Mute, "color", (255, 0, 0)),
        ):  # Red color
            mute = Mute(mock_hardware)

            # This should not raise an exception and should return bytes
            result = bytes(mute)
            assert isinstance(result, bytes)

    def test_mute_specific_properties_override(self) -> None:
        """Test that Mute-specific properties properly override Flag properties."""
        mock_hardware = create_mock_mute_hardware()

        with patch.object(mock_hardware, "acquire"), patch.object(Mute, "reset"):
            mute = Mute(mock_hardware)

            # Mute should override is_button to return True
            assert mute.is_button is True

            # Mute should have button_on property (not in base Flag)
            # Check that the property exists in the class, not the instance
            assert "button_on" in dir(Mute)
            assert isinstance(Mute.button_on, property)


class TestLuxaforMuteEdgeCases:
    """Test edge cases and error conditions for Luxafor Mute."""

    def test_button_on_read_strategy_exception(self) -> None:
        """Test button_on when read_strategy raises an exception."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(
                Mute,
                "read_strategy",
                side_effect=Exception("Device communication error"),
            ),
        ):
            mute = Mute(mock_hardware)

            # Should not crash, but may raise the exception or return a default value
            # The current implementation doesn't handle this case, so it will raise
            with pytest.raises(Exception, match="Device communication error"):
                assert mute.button_on

    def test_button_on_none_response(self) -> None:
        """Test button_on when read_strategy returns None."""
        mock_hardware = create_mock_mute_hardware()

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(Mute, "read_strategy", return_value=None),
        ):
            mute = Mute(mock_hardware)

            # This will likely cause a TypeError when trying to access None[0]
            with pytest.raises(TypeError):
                assert mute.button_on

    def test_multiple_button_reads(self) -> None:
        """Test multiple sequential button reads behave consistently."""
        mock_hardware = create_mock_mute_hardware()

        responses = [
            [131, 1, 0, 0, 0, 0, 0, 0],  # Button pressed
            [131, 0, 0, 0, 0, 0, 0, 0],  # Button released
            [66, 0, 0, 0, 0, 0, 0, 0],  # Status response
        ]

        with (
            patch.object(mock_hardware, "acquire"),
            patch.object(Mute, "reset"),
            patch.object(Mute, "read_strategy", side_effect=responses) as mock_read,
        ):
            mute = Mute(mock_hardware)

            # First read - button pressed
            assert mute.button_on is True

            # Second read - button released
            assert mute.button_on is False

            # Third read - status response, sets _button = False
            result = mute.button_on
            assert result is False

            # Verify all calls were made with correct parameters
            assert mock_read.call_count == 3
            for call in mock_read.call_args_list:
                assert call[0] == (8, 200)

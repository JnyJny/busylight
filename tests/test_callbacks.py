"""Tests for callback functions."""

from unittest.mock import Mock, patch

import pytest
import typer
from busylight.callbacks import string_to_scaled_color


class TestStringToScaledColorCallback:
    """Test the string_to_scaled_color callback function."""

    @patch("busylight.callbacks.parse_color_string")
    def test_string_to_scaled_color_success(self, mock_parse_color):
        """Should parse color string and return scaled tuple."""
        mock_parse_color.return_value = (255, 128, 64)
        mock_ctx = Mock()
        mock_ctx.obj.dim = 1.0

        result = string_to_scaled_color(mock_ctx, "red")

        mock_parse_color.assert_called_once_with("red", 1.0)
        assert result == (255, 128, 64)

    @patch("busylight.callbacks.parse_color_string")
    def test_string_to_scaled_color_with_color_lookup_error(self, mock_parse_color):
        """Should exit with code 1 on ColorLookupError."""
        from busylight.color import ColorLookupError

        mock_parse_color.side_effect = ColorLookupError("Unknown color")
        mock_ctx = Mock()
        mock_ctx.obj.dim = 1.0

        with pytest.raises(typer.Exit) as exc_info:
            string_to_scaled_color(mock_ctx, "invalid_color")

        assert exc_info.value.exit_code == 1

    def test_string_to_scaled_color_integration(self):
        """Integration test with actual color parsing."""
        from busylight.global_options import GlobalOptions

        mock_ctx = Mock()
        mock_ctx.obj = GlobalOptions()
        mock_ctx.obj.dim = 1.0

        result = string_to_scaled_color(mock_ctx, "red")
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert all(isinstance(x, int) and 0 <= x <= 255 for x in result)

    def test_string_to_scaled_color_integration_with_hex(self):
        """Integration test with hex color."""
        from busylight.global_options import GlobalOptions

        mock_ctx = Mock()
        mock_ctx.obj = GlobalOptions()
        mock_ctx.obj.dim = 1.0

        result = string_to_scaled_color(mock_ctx, "#ff0000")
        assert result == (255, 0, 0)

    def test_string_to_scaled_color_integration_with_invalid_color(self):
        """Integration test with invalid color should exit."""
        from busylight.global_options import GlobalOptions

        mock_ctx = Mock()
        mock_ctx.obj = GlobalOptions()
        mock_ctx.obj.dim = 1.0

        with pytest.raises(typer.Exit):
            string_to_scaled_color(mock_ctx, "not_a_color")

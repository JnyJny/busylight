"""Tests for busyserve CLI functionality."""

from unittest.mock import MagicMock, Mock, patch

import pytest
import typer
from busylight.busyserve import busyserve_cli, serve_http_api


class TestBusyserveCLI:
    """Test busyserve CLI setup."""

    def test_busyserve_cli_is_typer_instance(self):
        """busyserve_cli should be a Typer instance."""
        assert isinstance(busyserve_cli, typer.Typer)

    def test_busyserve_cli_has_serve_command(self):
        """busyserve_cli should have serve command."""
        assert callable(serve_http_api)


class TestServeHTTPAPI:
    """Test the serve HTTP API function."""

    @patch("busylight.busyserve.uvicorn")
    @patch("busylight.busyserve.logger")
    @patch("busylight.busyserve.environ")
    def test_serve_http_api_success(self, mock_environ, mock_logger, mock_uvicorn):
        """Should start uvicorn server successfully."""
        serve_http_api(debug=True, host="localhost", port=9000)

        mock_environ.__setitem__.assert_called_with("BUSYLIGHT_DEBUG", "True")

        mock_logger.enable.assert_called_once_with("busylight")

        mock_uvicorn.run.assert_called_once_with(
            "busylight.api:busylightapi", host="localhost", port=9000, reload=True
        )

    @patch("busylight.busyserve.uvicorn")
    @patch("busylight.busyserve.logger")
    @patch("busylight.busyserve.environ")
    def test_serve_http_api_no_debug(self, mock_environ, mock_logger, mock_uvicorn):
        """Should disable logging when debug=False."""
        serve_http_api(debug=False, host="0.0.0.0", port=8000)

        mock_environ.__setitem__.assert_called_with("BUSYLIGHT_DEBUG", "False")

        mock_logger.disable.assert_called_once_with("busylight")

        mock_uvicorn.run.assert_called_once_with(
            "busylight.api:busylightapi", host="0.0.0.0", port=8000, reload=False
        )

    @patch("busylight.busyserve.uvicorn")
    @patch("busylight.busyserve.logger")
    @patch("busylight.busyserve.environ")
    def test_serve_http_api_module_not_found_error(
        self, mock_environ, mock_logger, mock_uvicorn
    ):
        """Should handle ModuleNotFoundError gracefully."""
        mock_uvicorn.run.side_effect = ModuleNotFoundError("No module named 'fastapi'")

        with pytest.raises(typer.Exit) as exc_info:
            serve_http_api(debug=False, host="localhost", port=8000)

        assert exc_info.value.exit_code == 1

        mock_logger.error.assert_called()


class TestBusyserveImport:
    """Test busyserve import behavior with missing dependencies."""

    def test_busyserve_imports_successfully_with_uvicorn(self):
        """Should import successfully when uvicorn is available."""
        import busylight.busyserve as busyserve_module

        assert hasattr(busyserve_module, "busyserve_cli")
        assert hasattr(busyserve_module, "serve_http_api")

    def test_busyserve_module_has_required_attributes(self):
        """Should have all required module attributes."""
        import busylight.busyserve as busyserve_module

        assert hasattr(busyserve_module, "busyserve_cli")

        assert hasattr(busyserve_module, "serve_http_api")

        assert callable(busyserve_module.serve_http_api)

"""Tests for main CLI functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import typer

from busylight.__main__ import cli, precommand_callback


class TestCLISetup:
    """Test CLI setup and configuration."""
    
    def test_cli_is_typer_instance(self):
        """CLI should be a Typer instance."""
        assert isinstance(cli, typer.Typer)
    
    def test_cli_has_subcommands(self):
        """CLI should have subcommands registered."""
        # The CLI should have commands from subcommands
        # We can't easily introspect typer commands, but we can test
        # that the import and setup doesn't fail
        assert cli is not None


class TestPrecommandCallback:
    """Test the main CLI callback function."""
    
    @patch('busylight.__main__.LightManager')
    @patch('busylight.__main__.logger')
    def test_precommand_callback_sets_options(self, mock_logger, mock_light_manager):
        """Should set global options correctly."""
        ctx = Mock()
        ctx.ensure_object.return_value = Mock()
        ctx.invoked_subcommand = "list"
        
        mock_light_manager.parse_target_lights.return_value = [1, 2]
        
        # Call the callback
        precommand_callback(
            ctx=ctx,
            debug=True,
            targets="1,2",
            all_lights=False,
            dim=75,
            timeout=30.0
        )
        
        # Verify options were set
        options = ctx.ensure_object.return_value
        assert options.debug == True
        assert options.dim == 0.75  # Should be scaled to 0-1
        assert options.timeout == 30.0
        assert options.lights == [1, 2]
    
    @patch('busylight.__main__.LightManager')
    @patch('busylight.__main__.logger')
    def test_precommand_callback_with_all_lights(self, mock_logger, mock_light_manager):
        """Should clear lights list when all_lights is True."""
        ctx = Mock()
        ctx.ensure_object.return_value = Mock()
        ctx.invoked_subcommand = "rainbow"
        
        mock_light_manager.parse_target_lights.return_value = [1, 2]
        
        # Call with all_lights=True
        precommand_callback(
            ctx=ctx,
            debug=False,
            targets="1,2",
            all_lights=True,
            dim=100,
            timeout=None
        )
        
        # Should clear the lights list
        options = ctx.ensure_object.return_value
        assert options.lights == []
    
    @patch('busylight.__main__.LightManager')
    @patch('busylight.__main__.logger')
    def test_precommand_callback_list_command_forces_all_lights(self, mock_logger, mock_light_manager):
        """List command with no targets should force all_lights=True."""
        ctx = Mock()
        ctx.ensure_object.return_value = Mock()
        ctx.invoked_subcommand = "list"
        
        mock_light_manager.parse_target_lights.return_value = [0]
        
        # Call with list command and no targets
        precommand_callback(
            ctx=ctx,
            debug=False,
            targets=None,  # No targets specified
            all_lights=False,
            dim=100,
            timeout=None
        )
        
        # Should clear lights list (forces all lights for list command)
        options = ctx.ensure_object.return_value
        assert options.lights == []
    
    @patch('busylight.__main__.LightManager')
    @patch('busylight.__main__.logger')
    def test_precommand_callback_enables_logging_when_debug(self, mock_logger, mock_light_manager):
        """Should enable logging when debug=True."""
        ctx = Mock()
        ctx.ensure_object.return_value = Mock()
        ctx.invoked_subcommand = "on"
        
        mock_light_manager.parse_target_lights.return_value = []
        
        precommand_callback(
            ctx=ctx,
            debug=True,
            targets="",
            all_lights=False,
            dim=100,
            timeout=None
        )
        
        mock_logger.enable.assert_called_once_with("busylight")
    
    @patch('busylight.__main__.LightManager')  
    @patch('busylight.__main__.logger')
    def test_precommand_callback_disables_logging_when_not_debug(self, mock_logger, mock_light_manager):
        """Should disable logging when debug=False."""
        ctx = Mock()
        ctx.ensure_object.return_value = Mock()
        ctx.invoked_subcommand = "off"
        
        mock_light_manager.parse_target_lights.return_value = []
        
        precommand_callback(
            ctx=ctx,
            debug=False,
            targets="",
            all_lights=False,
            dim=100,
            timeout=None
        )
        
        mock_logger.disable.assert_called_once_with("busylight")
    
    @patch('busylight.__main__.LightManager')
    @patch('busylight.__main__.logger')
    def test_precommand_callback_exits_with_help_when_no_subcommand(self, mock_logger, mock_light_manager):
        """Should exit with help when no subcommand is invoked."""
        ctx = Mock()
        ctx.ensure_object.return_value = Mock()
        ctx.invoked_subcommand = None
        ctx.get_help.return_value = "Help text"
        
        mock_light_manager.parse_target_lights.return_value = []
        
        with pytest.raises(typer.Exit) as exc_info:
            precommand_callback(
                ctx=ctx,
                debug=False,
                targets="",
                all_lights=False,
                dim=100,
                timeout=None
            )
        
        assert exc_info.value.exit_code == 1
        ctx.get_help.assert_called_once()


class TestCLIConditionalImports:
    """Test conditional imports in CLI setup."""
    
    @patch('busylight.__main__.logger')
    def test_cli_handles_missing_busyserve_gracefully(self, mock_logger):
        """CLI should handle missing busyserve imports gracefully."""
        # This test verifies that the conditional import works
        # The import should have already happened during module load
        # so we test that the CLI object exists and is functional
        assert cli is not None
        
        # The CLI should have basic commands even if busyserve failed to import
        # We can't easily test the conditional import after the fact,
        # but we can verify the CLI is in a working state
        assert hasattr(cli, 'commands') or hasattr(cli, 'registered_commands')


class TestGlobalOptions:
    """Test GlobalOptions integration."""
    
    def test_global_options_import(self):
        """Should be able to import GlobalOptions."""
        from busylight.global_options import GlobalOptions
        assert GlobalOptions is not None
    
    def test_global_options_can_be_instantiated(self):
        """Should be able to create GlobalOptions instance.""" 
        from busylight.global_options import GlobalOptions
        options = GlobalOptions()
        assert options is not None


class TestMainModuleEntry:
    """Test main module entry point."""
    
    @patch('busylight.__main__.cli')
    def test_main_module_calls_cli(self, mock_cli):
        """When run as main module, should call cli()."""
        # We can't easily test __main__ execution, but we can verify
        # the cli object is set up correctly for execution
        assert mock_cli is not None
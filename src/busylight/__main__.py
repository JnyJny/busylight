"""Busylight command-line interface.

This module implements the main CLI application for controlling USB LED lights.
It uses the Typer framework to provide a command-line interface with global
options and subcommands for different light operations.

The CLI supports:
- Global options for light selection, timeout, dimming, and debugging
- Subcommands for turning lights on/off, blinking, effects, and configuration
- Context management for passing options between commands
- Conditional loading of web server components

Example:
    Basic CLI usage::

        # Turn on all lights with red color
        busylight on red

        # Blink specific lights
        busylight -l 0,1 blink green --count 5

        # List available lights
        busylight list
"""

from typing import Optional

import typer
from loguru import logger

from . import __version__
from .callbacks import string_to_scaled_color
from .global_options import GlobalOptions
from .speed import Speed
from .subcommands import subcommands

cli = typer.Typer()

for subcommand in subcommands:
    cli.add_typer(subcommand)

try:
    from .busyserve import busyserve_cli

    cli.add_typer(busyserve_cli)
except ImportError:
    pass

webcli = typer.Typer()


@cli.callback(invoke_without_command=True, no_args_is_help=True)
def precommand_callback(
    ctx: typer.Context,
    debug: bool = typer.Option(
        False,
        "--debug",
        "-D",
        help="Enable debugging output.",
    ),
    targets: str = typer.Option(
        None,
        "--light-id",
        "-l",
        help="Specify a light or lights to act on.",
    ),
    all_lights: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Use all connected lights.",
    ),
    dim: int = typer.Option(
        100,
        "--dim",
        "-d",
        min=0,
        max=100,
        clamp=True,
        help="Scale color intensity by percentage.",
    ),
    timeout: float = typer.Option(
        None,
        "--timeout",
        show_default=True,
        help="Time out command in seconds.",
    ),
) -> None:
    """Control USB connected presence lights.

    :param ctx: Typer context for sharing state between commands
    :param debug: Enable debug logging output
    :param targets: Comma-separated list of light indices to target
    :param all_lights: Override target selection to use all lights
    :param dim: Brightness percentage from 0-100
    :param timeout: Maximum operation duration in seconds

    This callback function processes global CLI options and sets up the
    application state before any subcommand runs. It handles:

    - Parsing light target specifications
    - Configuring logging based on debug flag
    - Setting up the global options object
    - Special handling for the 'list' command with no targets

    The function exits with help text if no subcommand is specified.
    """
    (logger.enable if debug else logger.disable)("busylight")

    options = ctx.ensure_object(GlobalOptions)

    options.debug = debug
    options.dim = dim / 100
    options.timeout = timeout
    options.lights = []

    if ctx.invoked_subcommand == "list" and targets is None:
        all_lights = True

    # Parse light targets - simple conversion for now
    if targets:
        # Convert comma-separated string to list of indices
        try:
            options.lights = [int(x.strip()) for x in targets.split(",")]
        except ValueError:
            # If parsing fails, use empty list (all lights)
            options.lights = []

    logger.info(f"version {__version__}")
    logger.info(f"timeout={options.timeout}")
    logger.info(f"    dim={options.dim}")
    logger.info(f" lights={options.lights}")
    logger.info(f"    cmd={ctx.invoked_subcommand!r}")

    if all_lights:
        options.lights.clear()

    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit(code=1)


if __name__ == "__main__":
    exit(cli())

"""Busylight command-line interface"""

from typing import Optional

import typer
from loguru import logger

from . import __version__
from .busyserve import busyserve_cli
from .callbacks import string_to_scaled_color
from .effects import Effects
from .global_options import GlobalOptions
from .manager import LightManager
from .speed import Speed
from .subcommands import subcommands

cli = typer.Typer()

for subcommand in subcommands:
    cli.add_typer(subcommand)

cli.add_typer(busyserve_cli)

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
    """Control USB connected presense lights."""
    (logger.enable if debug else logger.disable)("busylight")

    options = ctx.ensure_object(GlobalOptions)

    options.debug = debug
    options.dim = dim / 100
    options.timeout = timeout
    options.lights = []

    if ctx.invoked_subcommand == "list" and targets is None:
        all_lights = True

    options.lights.extend(LightManager.parse_target_lights(targets))

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

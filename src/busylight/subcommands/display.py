"""Busylight Display Command Line Interface"""

from typing import Optional

import typer
from busylight_core import Light, LightUnavailableError, NoLightsFoundError
from loguru import logger

display_cli = typer.Typer()


@display_cli.command(name="list")
def list_lights(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information about each light.",
        show_default=True,
    ),
) -> None:
    """List currently connected lights."""

    logger.info("Listing connected lights.")
    try:
        lights = ctx.obj.manager.selected_lights(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("No lights detected.", fg="red")
        raise typer.Exit(code=1) from None

    for index, light in enumerate(lights):
        typer.secho(f"{index:3d} ", nl=False, fg="red")
        typer.secho(light.name, fg="green")
        if verbose:
            for key, value in light.hardware.__dict__.items():
                if key == "handle":
                    continue
                typer.secho(f"    {key}: ", nl=False, fg="black")
                typer.secho(f"{value}", fg="blue")


@display_cli.command(name="supported")
def list_supported_lights(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print vendor and product identifiers.",
    ),
) -> None:
    """List supported lights."""
    logger.info("listing supported lights")

    if not verbose:
        for vendor, names in Light.supported_lights().items():
            typer.secho(vendor, fg="blue")
            for name in names:
                typer.secho("  - ", nl=False)
                typer.secho(name, fg="green")
        raise typer.Exit()

    supported_lights = {}
    for subclass in Light.subclasses():
        supported_lights.setdefault(subclass.vendor(), []).append(subclass)

    for vendor, subclasses in supported_lights.items():
        for subclass in subclasses:
            typer.secho(subclass.vendor(), fg="blue")
            for (vid, pid), name in subclass.supported_device_ids.items():
                typer.secho("  - ", nl=False)
                typer.secho(f"0x{vid:04x}:0x{pid:04x} ", fg="red", nl=False)
                typer.secho(name, fg="green")

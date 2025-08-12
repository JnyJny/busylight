"""Busylight Display Command Line Interface.

This module implements display-related subcommands for listing and inspecting
connected lights and supported devices. It provides both basic and verbose
output modes for different use cases.

The module includes:
- Listing currently connected lights with optional verbose details
- Displaying supported light devices and their identifiers
- Hardware information display for connected devices

Example:
    List connected lights::

        busylight list
        busylight list --verbose

    Show supported devices::

        busylight supported
        busylight supported --verbose
"""

from typing import Optional

import typer
from busylight_core import Light, LightUnavailableError, NoLightsFoundError
from loguru import logger

from .helpers import get_light_selection

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
    """List currently connected lights.

    :param ctx: Typer context containing global options and controller
    :param verbose: Whether to show detailed hardware information

    Displays all currently connected and accessible lights. In normal mode,
    shows the index and name of each light. In verbose mode, additionally
    shows hardware details like vendor ID, product ID, and other device
    properties.

    The command exits with an error if no lights are detected.
    """

    logger.info("Listing connected lights.")
    try:
        selection = get_light_selection(ctx)
        lights = selection.lights
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
    """List supported lights and devices.

    :param verbose: Whether to show vendor/product IDs and technical details

    Displays all light devices supported by the busylight-core library.
    In normal mode, shows vendor names and device names organized by
    manufacturer. In verbose mode, additionally shows vendor IDs, product
    IDs, and other technical identifiers.

    This command is useful for identifying which devices are compatible
    before attempting to use them.
    """
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

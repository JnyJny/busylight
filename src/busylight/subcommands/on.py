"""On Command Line Interface"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color
from .helpers import get_light_selection

on_cli = typer.Typer()


@on_cli.command(name="on")
def activate_lights(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument(
        "green",
        callback=string_to_scaled_color,
        show_default=True,
    ),
) -> None:
    """Activate lights with a color."""
    logger.info("Activating lights with color: {}", color)

    try:
        selection = get_light_selection(ctx)
        selection.turn_on(color)
    except (KeyboardInterrupt, TimeoutError):
        selection = get_light_selection(ctx)
        selection.turn_off()
    except NoLightsFoundError:
        typer.secho("No lights found.", fg="red")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error activating lights: {e}", fg="red")
        raise typer.Exit(code=1)

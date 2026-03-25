"""Off Command Line Interface.

This module implements the 'off' subcommand for turning off lights and
stopping any running effects. It provides a simple way to deactivate
lights and clean up their state.

The command supports:
- Turning off selected lights
- Canceling any running light tasks/effects
- Graceful error handling for unavailable lights
- Integration with the global light selection system

Example:
    Turn off lights::

        busylight off          # Turn off all lights
        busylight -l 0,1 off   # Turn off specific lights
"""

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from ..callbacks import string_to_scaled_color
from .helpers import get_light_selection

off_cli = typer.Typer()


@off_cli.command(name="off")
def deactivate_lights(ctx: typer.Context) -> None:
    """Deactivate lights and stop any running effects.

    :param ctx: Typer context containing global options and controller

    This command turns off all selected lights and cancels any running
    tasks or effects. It's useful for quickly stopping all light activity
    and returning lights to their default off state.

    The command handles cases where no lights are found gracefully by
    displaying an informational message rather than failing with an error.
    """

    logger.info("Deactivating lights")

    try:
        selection = get_light_selection(ctx)
        selection.turn_off()
    except NoLightsFoundError:
        typer.secho("No lights to turn off.", fg="red")

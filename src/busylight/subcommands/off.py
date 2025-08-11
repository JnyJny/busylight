"""Off Command Line Interface"""

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from ..callbacks import string_to_scaled_color
from .helpers import get_light_selection

off_cli = typer.Typer()


@off_cli.command(name="off")
def deactivate_lights(ctx: typer.Context) -> None:
    """Deactivate lights."""

    logger.info("Deactivating lights")

    try:
        selection = get_light_selection(ctx)
        selection.turn_off()
    except NoLightsFoundError:
        typer.secho("No lights to turn off.", fg="red")

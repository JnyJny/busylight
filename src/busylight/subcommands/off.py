"""Off Command Line Interface"""

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from ..callbacks import string_to_scaled_color

off_cli = typer.Typer()


@off_cli.command(name="off")
def deactivate_lights(ctx: typer.Context) -> None:
    """Deactivate lights."""

    logger.info("Deactivating lights")

    try:
        ctx.obj.manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("No lights to turn off.", fg="red")

"""On Command with new LightController."""

from typing import Optional

import typer
from busylight_core import NoLightsFoundError
from loguru import logger

on_cli = typer.Typer()


@on_cli.command(name="on")
def activate_lights(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument(
        "green",
        show_default=True,
    ),
) -> None:
    """Activate lights with a color."""
    logger.info("Activating lights with color: {}", color)

    try:
        with ctx.obj.controller as controller:
            # Select lights based on global options
            if ctx.obj.lights:
                selection = controller.by_index(*ctx.obj.lights)
            else:
                selection = controller.all()

            if not selection:
                typer.secho("No lights found.", fg="red")
                raise typer.Exit(code=1)

            # Turn on lights with the new fluent interface
            selection.turn_on(color, timeout=ctx.obj.timeout)

    except (KeyboardInterrupt, TimeoutError):
        # Automatic cleanup happens in context manager
        logger.info("Operation interrupted")
    except NoLightsFoundError:
        typer.secho("No lights found.", fg="red")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error activating lights: {e}", fg="red")
        raise typer.Exit(code=1)

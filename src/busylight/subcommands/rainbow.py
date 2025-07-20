"""Rainbow Command Line Interface"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color
from busylight.effects import Effects
from busylight.speed import Speed

rainbow_cli = typer.Typer()


@rainbow_cli.command(name="rainbow")
def rainbow_lights(
    ctx: typer.Context,
    speed: Speed = typer.Option(
        Speed.Slow,
        "--speed",
        "-s",
        help="Speed of the rainbow effect.",
        show_default=True,
    ),
    count: int = typer.Option(
        0,
        "--count",
        "-c",
        help="Number of rainbows. 0 means infinite.",
        show_default=True,
    ),
) -> None:
    """LEDs lights love rainbows."""
    logger.info("Applying rainbow effect.")

    effect = Effects.for_name("spectrum")(
        speed.duty_cycle / 4,
        scale=ctx.obj.dim,
        count=count,
    )

    try:
        ctx.obj.manager.apply_effect(effect, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        ctx.obj.manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("Unable to rainbow lights.", fg="red")
        raise typer.Exit(code=1)
    except Exception as error:
        typer.secho(f"Error rainbow lights: {error}", fg="red")
        raise typer.Exit(code=1)

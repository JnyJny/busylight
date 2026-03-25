"""Rainbow Command Line Interface"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color
from busylight.effects import Spectrum
from busylight.speed import Speed

from .helpers import get_light_selection

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
    led: int = typer.Option(
        0,
        "--led",
        help="Target LED index (0=all LEDs, 1+=specific LED for multi-LED devices)",
        show_default=True,
    ),
) -> None:
    """LEDs lights love rainbows."""
    logger.info("Applying rainbow effect.")

    effect = Spectrum(
        scale=ctx.obj.dim,
        count=count,
    )

    try:
        selection = get_light_selection(ctx)
        selection.apply_effect(
            effect, duration=ctx.obj.timeout, interval=speed.duty_cycle / 4, led=led
        )
    except (KeyboardInterrupt, TimeoutError):
        selection = get_light_selection(ctx)
        selection.turn_off()
    except NoLightsFoundError:
        typer.secho("Unable to rainbow lights.", fg="red")
        raise typer.Exit(code=1)
    except Exception as error:
        typer.secho(f"Error rainbow lights: {error}", fg="red")
        raise typer.Exit(code=1)

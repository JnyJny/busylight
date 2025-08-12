"""Pulse Command Line Interface"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color
from busylight.effects import Effects
from busylight.speed import Speed

from .helpers import get_light_selection

pulse_cli = typer.Typer()


@pulse_cli.command(name="pulse")
def pulse_lights(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument(
        "green",
        callback=string_to_scaled_color,
        help="Color of the pulse effect.",
        show_default=True,
    ),
    speed: Speed = typer.Option(
        Speed.Slow,
        "--speed",
        "-s",
        help="Speed of the pulse effect.",
        show_default=True,
    ),
    count: int = typer.Option(
        0,
        "--count",
        "-c",
        help="Number of pulses. 0 means infinite.",
        show_default=True,
    ),
    led: int = typer.Option(
        0,
        "--led",
        help="Target LED index (0=all LEDs, 1+=specific LED for multi-LED devices)",
        show_default=True,
    ),
) -> None:
    """Pulse lights with a specified color and speed."""

    logger.info("Applying pulse effect.")

    effect = Effects.for_name("gradient")(color, step=8, count=count)

    try:
        selection = get_light_selection(ctx)
        selection.apply_effect(
            effect, duration=ctx.obj.timeout, interval=speed.duty_cycle / 16, led=led
        )
    except (KeyboardInterrupt, TimeoutError):
        selection = get_light_selection(ctx)
        selection.turn_off()
    except NoLightsFoundError:
        typer.secho("Unable to pulse lights.", fg="red")
        raise typer.Exit(code=1)
    except Exception as error:
        typer.secho(f"Error pulse lights: {error}", fg="red")
        raise typer.Exit(code=1)

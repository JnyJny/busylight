"""Pulse Command Line Interface"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color
from busylight.effects import Effects
from busylight.speed import Speed

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
) -> None:
    """Pulse lights with a specified color and speed."""

    logger.info("Applying pulse effect.")

    effect = Effects.for_name("gradient")(color, speed.duty_cycle / 16, 8, count=count)

    try:
        ctx.obj.manager.apply_effect(effect, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        ctx.obj.manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("Unable to pulse lights.", fg="red")
        raise typer.Exit(code=1)
    except Exception as error:
        typer.secho(f"Error pulse lights: {error}", fg="red")
        raise typer.Exit(code=1)

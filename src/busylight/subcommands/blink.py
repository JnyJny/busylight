"""Blink Command Line Interface"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color
from busylight.effects import Effects
from busylight.speed import Speed

blink_cli = typer.Typer()


@blink_cli.command(name="blink")
def blink_lights(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument(
        "red",
        callback=string_to_scaled_color,
        show_default=True,
        help="Color of the blink effect.",
    ),
    speed: Speed = typer.Option(
        Speed.Slow,
        "--speed",
        "-s",
        show_default=True,
        help="Blink speed",
    ),
    count: int = typer.Option(
        0,
        "--count",
        "-c",
        show_default=True,
        help="Number of blinks. 0 means infinite.",
    ),
) -> None:
    """Blink lights."""
    logger.info("Blinking lights with color: {}", color)

    effect = Effects.for_name("blink")(color, speed.duty_cycle, count=count)

    try:
        ctx.obj.manager.apply_effect(effect, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        ctx.obj.manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("Unable to blink lights.", fg="red")
        raise typer.Exit(code=1)
    except Exception as error:
        typer.secho(f"Error blinking lights: {error}", fg="red")
        raise typer.Exit(code=1)

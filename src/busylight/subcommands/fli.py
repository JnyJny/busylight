"""Fli Command Line Interface"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color
from busylight.effects import Effects
from busylight.speed import Speed

fli_cli = typer.Typer()


@fli_cli.command(name="fli")
def flash_lights_impressively(
    ctx: typer.Context,
    on_color: Optional[str] = typer.Argument(
        "red",
        callback=string_to_scaled_color,
        help="Primary color of the fli effect.",
        show_default=True,
    ),
    off_color: Optional[str] = typer.Argument(
        "blue",
        callback=string_to_scaled_color,
        help="Secondary color of the fli effect.",
        show_default=True,
    ),
    speed: Speed = typer.Option(
        Speed.Slow,
        "--speed",
        "-s",
        help="Speed of the fli effect.",
        show_default=True,
    ),
    count: int = typer.Option(
        0,
        "--count",
        "-c",
        help="Number of cycles. 0 means infinite.",
        show_default=True,
    ),
) -> None:
    """Flash Lights Impressively"""

    logger.info("Applying fli effect.")

    effect = Effects.for_name("blink")(
        on_color,
        speed.duty_cycle / 10,
        off_color=off_color,
        count=count,
    )

    try:
        ctx.obj.manager.apply_effect(effect, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        ctx.obj.manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("Unable to flash lights impressively.", fg="red")
        raise typer.Exit(code=1)
    except Exception as error:
        typer.secho(f"Error while flashing lights impressively: {error}", fg="red")
        raise typer.Exit(code=1)

"""Fli Command Line Interface"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color
from busylight.effects import Effects
from busylight.speed import Speed

from .helpers import get_light_selection

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
    led: int = typer.Option(
        0,
        "--led",
        help="Target LED index (0=all LEDs, 1+=specific LED for multi-LED devices)",
        show_default=True,
    ),
) -> None:
    """Flash Lights Impressively"""

    logger.info("Applying fli effect.")

    effect = Effects.for_name("blink")(
        on_color,
        off_color=off_color,
        count=count,
    )

    try:
        selection = get_light_selection(ctx)
        selection.apply_effect(
            effect, duration=ctx.obj.timeout, interval=speed.duty_cycle / 10, led=led
        )
    except (KeyboardInterrupt, TimeoutError):
        selection = get_light_selection(ctx)
        selection.turn_off()
    except NoLightsFoundError:
        typer.secho("Unable to flash lights impressively.", fg="red")
        raise typer.Exit(code=1)
    except Exception as error:
        typer.secho(f"Error while flashing lights impressively: {error}", fg="red")
        raise typer.Exit(code=1)

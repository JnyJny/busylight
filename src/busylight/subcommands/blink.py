"""Blink Command Line Interface.

This module implements the 'blink' subcommand for creating blinking light
effects. It supports customizable colors, blink counts, and speeds, making
it useful for notifications and visual feedback.

The command supports:
- Color specification in multiple formats
- Configurable blink count (finite or infinite)
- Speed control (slow, medium, fast)
- Graceful interrupt handling

Example:
    Create various blinking effects::

        busylight blink red
        busylight blink blue --count 5 --speed fast
        busylight blink "#00ff00" --count 0  # Infinite blinking
"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color
from busylight.effects import Effects
from busylight.speed import Speed

from .helpers import get_light_selection

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
    led: int = typer.Option(
        0,
        "--led",
        help="Target LED index (0=all LEDs, 1+=specific LED for multi-LED devices)",
        show_default=True,
    ),
) -> None:
    """Create a blinking effect on selected lights.

    :param ctx: Typer context containing global options and controller
    :param color: Color specification for the blink effect
    :param speed: Blink speed (slow, medium, or fast)
    :param count: Number of blinks. 0 means infinite blinking
    :param led: Target LED index for multi-LED devices

    This command applies a blinking effect to the selected lights using
    the specified color, speed, and count. For devices with multiple LEDs
    (like Blink1 mk2), use --led to target specific LEDs.

    The effect runs asynchronously and can be interrupted with Ctrl+C.
    For infinite blinking (count=0), the command will continue until
    interrupted. For finite counts, the command exits after the specified
    number of blinks complete.

    Example:
        Target specific LEDs::

            busylight blink red --led 1 --count 3    # Top LED only
            busylight blink green --led 2            # Bottom LED infinite
    """
    logger.info("Blinking lights with color: {}", color)

    try:
        selection = get_light_selection(ctx)
        selection.blink(color, count=count, speed=speed.name.lower(), led=led)
    except (KeyboardInterrupt, TimeoutError):
        selection = get_light_selection(ctx)
        selection.turn_off()
    except NoLightsFoundError:
        typer.secho("Unable to blink lights.", fg="red")
        raise typer.Exit(code=1)
    except Exception as error:
        typer.secho(f"Error blinking lights: {error}", fg="red")
        raise typer.Exit(code=1)

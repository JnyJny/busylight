"""On Command Line Interface.

This module implements the 'on' subcommand for turning lights on with a
specified color. It includes special handling for Kuando lights that require
keepalive tasks to maintain their connection.

The command supports:
- Basic color specification (named colors, hex values, RGB tuples)
- Kuando light keepalive task management
- Graceful error handling and cleanup
- Integration with the global light controller

Example:
    Turn lights on with different colors::

        busylight on red
        busylight on "#ff0000"
        busylight on --color green
"""

from typing import Optional

import typer
from busylight_core import LightUnavailableError, NoLightsFoundError
from loguru import logger

from busylight.callbacks import string_to_scaled_color

from .helpers import get_light_selection

on_cli = typer.Typer()


@on_cli.command(name="on")
def activate_lights(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument(
        "green",
        callback=string_to_scaled_color,
        show_default=True,
    ),
    led: int = typer.Option(
        0,
        "--led",
        help="Target LED index (0=all LEDs, 1+=specific LED for multi-LED devices)",
        show_default=True,
    ),
) -> None:
    """Activate lights with a specified color.

    :param ctx: Typer context containing global options and controller
    :param color: Color specification (name, hex, or RGB tuple)
    :param led: Target LED index for multi-LED devices

    This command turns on the selected lights with the specified color.
    For devices with multiple LEDs (like Blink1 mk2), use --led to target
    specific LEDs: 0=all LEDs, 1=first/top LED, 2=second/bottom LED, etc.

    It includes special handling for Kuando lights which require keepalive
    tasks to maintain their USB connection. When Kuando lights are detected,
    the command will continue running until interrupted to keep the lights
    active.

    The command handles various error conditions gracefully, including
    keyboard interrupts, timeouts, and device unavailability.

    Example:
        Turn on lights with different color formats::

            busylight on red
            busylight on "#ff0000"
            busylight on "rgb(255,0,0)"

        Target specific LEDs on multi-LED devices::

            busylight on red --led 1      # Top LED only
            busylight on blue --led 2     # Bottom LED only
            busylight on green --led 0    # All LEDs (default)
    """
    logger.info("Activating lights with color: {}", color)

    try:
        controller = ctx.obj.controller
        selection = get_light_selection(ctx)

        kuando_lights = [
            light
            for light in selection.lights
            if "kuando" in light.__class__.__module__.lower()
        ]

        if kuando_lights:
            import asyncio

            async def turn_on_and_wait() -> None:
                selection.turn_on(color, led=led)

                while True:
                    all_tasks = []
                    for light in selection.lights:
                        all_tasks.extend(light.tasks.values())

                    if not all_tasks:
                        break

                    try:
                        await asyncio.wait(
                            all_tasks, return_when=asyncio.FIRST_COMPLETED
                        )
                    except KeyboardInterrupt:
                        for light in selection.lights:
                            light.cancel_tasks()
                        raise

            logger.info(
                "Kuando lights detected, keeping process alive (Ctrl+C to exit)"
            )
            asyncio.run(turn_on_and_wait())
        else:
            selection.turn_on(color, led=led)

    except (KeyboardInterrupt, TimeoutError):
        selection = get_light_selection(ctx)
        selection.turn_off()
    except NoLightsFoundError:
        typer.secho("No lights found.", fg="red")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error activating lights: {e}", fg="red")
        raise typer.Exit(code=1)

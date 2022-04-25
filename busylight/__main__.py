"""
"""

from dataclasses import dataclass
from contextlib import suppress
from enum import Enum
from pkg_resources import require as pkg_require

from typing import List, Optional

import typer
import webcolors

from loguru import logger

from .lights import USBLight, Speed
from .lights import NoLightsFound
from .color import ColorTuple, parse_color
from .effects import Effects
from .manager import LightManager

cli = typer.Typer()

webapi = typer.Typer()


lights: List[int] = []
manager = LightManager()
gTimeout: float

try:
    __version__: str = pkg_require("busylight-for-humans")[0].version
except Exception as error:
    logger.error(f"Failed to retrieve version string: {error}")
    __version__: str = "unknown"


def parse_target_lights(targets: str) -> List[int]:
    """Parses the `targets` string to produce a list of indicies.

    `lights` list with indices of lights that user wants to operate
    on. The targets string may be:
    - empty, meaning all lights
    - a single integer, specifying one line
    - [0-9]+[-:][0-9]+, specifying a range.
    """
    logger.debug(f"targets={targets}")

    lights = []
    for target in targets.split(","):
        logger.debug(f"target {target}")
        for sep in ["-", ":"]:
            if sep in target:
                logger.debug(f"found {sep} in {target}")
                start, _, end = target.partition(sep)
                logger.debug(f"building range {start} to {end}")
                lights.extend(list(range(int(start), int(end) + 1)))
                break
        else:
            with suppress(ValueError):
                lights.append(int(target))

    logger.debug(f"lights={lights}")
    return lights


def report_version(value: bool) -> None:
    """Prints the version string and exits."""
    if value:
        typer.secho(__version__, fg="blue")
        raise typer.Exit()


@cli.callback()
def global_callback(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", "-D", is_flag=True),
    targets: str = typer.Option("0", "--light-id", "-l"),
    all_lights: bool = typer.Option(False, "--all", "-a"),
    timeout: float = typer.Option(
        None,
        "--timeout",
        help="timeout in seconds",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        is_flag=True,
        is_eager=True,
        callback=report_version,
    ),
) -> None:
    """Control USB connected presense lights."""

    (logger.enable if debug else logger.disable)("busylight")
    logger.debug(f"version {__version__}")

    if not all_lights:
        lights.extend(parse_target_lights(targets))

    global gTimeout
    gTimeout = timeout
    logger.debug(f"gTimeout={gTimeout}")


@cli.command(name="on")
def turn_lights_on(
    color: Optional[str] = typer.Argument("green", callback=parse_color),
) -> None:
    """Activate lights.

    The default is green.
    """
    try:
        manager.on(color, lights, timeout=gTimeout)
    except KeyboardInterrupt:
        manager.off(lights)
    except NoLightsFound as error:
        typer.secho("No lights to turn on.", fg="red")
        raise typer.Exit(code=-1) from None


@cli.command(name="off")
def turn_lights_off() -> None:
    """Deactivate lights."""
    logger.debug("deactivating lights")

    try:
        manager.off(lights)
    except NoLightsFound as error:
        typer.secho(f"", fg="red")
        typer.secho("No lights to turn off.", fg="red")


@cli.command(name="blink")
def blink_lights(
    color: Optional[str] = typer.Argument("red", callback=parse_color),
    speed: Speed = typer.Argument(Speed.Slow),
) -> None:
    """Blink lights on and off.

    The default on color is red.
    """

    blink = Effects.for_name("blink")(color, speed.duty_cycle)

    try:
        manager.apply_effect(blink, lights, timeout=gTimeout)
    except KeyboardInterrupt:
        manager.off(lights)
    except NoLightsFound as error:
        typer.secho("Unable to blink lights.", fg="red")
        raise typer.Exit(code=-1) from None


@cli.command(name="rainbow")
def rainbow_lights(speed: Speed = typer.Argument(Speed.Slow)) -> None:
    """Display rainbow colors on specified lights."""

    rainbow = Effects.for_name("spectrum")(speed.duty_cycle / 4)

    try:
        manager.apply_effect(rainbow, lights, timeout=gTimeout)
    except KeyboardInterrupt:
        manager.off(lights)
    except NoLightsFound as error:
        typer.secho(f"No rainbow for you.", fg="red")
        raise typer.Exit(code=-1) from None


@cli.command(name="throb")
def throb_lights(
    color: Optional[str] = typer.Argument("red", callback=parse_color),
    speed: Speed = typer.Argument(Speed.Slow),
) -> None:
    """Throb light on and off.

    The default color is red."""

    throb = Effects.for_name("gradient")(color, speed.duty_cycle / 16, 8)
    try:
        manager.apply_effect(throb, lights, timeout=gTimeout)
    except KeyboardInterrupt:
        manager.off(lights)
    except NoLightsFound as error:
        typer.secho(f"Unable to throb lights.", fg="red")
        raise typer.Exit(code=-1) from None


@cli.command(name="fli")
def flash_lights_impressively(
    color_a: Optional[str] = typer.Argument("red", callback=parse_color),
    color_b: Optional[str] = typer.Argument("blue", callback=parse_color),
    speed: Speed = typer.Argument(Speed.Slow),
) -> None:
    """Flash lights quickly between two colors.

    The default colors are red and blue.

    Probably need some sort of trigger warning here.
    """

    fli = Effects.for_name("blink")(color_a, speed.duty_cycle / 10, off_color=color_b)

    try:
        manager.apply_effect(fli, lights, timeout=gTimeout)
    except KeyboardInterrupt:
        manager.off(lights)
    except NoLightsFound as error:
        typer.secho(f"Unable to flash lights impressively.", fg="red")
        raise typer.Exit(code=-1) from None


@cli.command(name="list")
def list_available_lights(
    verbose: bool = typer.Option(False, "--verbose", "-v", is_flag=True),
) -> None:
    """List currently connected lights.

    Lights in this list are currently plugged in and available for
    use. The `--verbose` flag will increase the amount of information
    displayed for each light. The global `--light-id` argument is ignored
    by this subcommand.
    """
    logger.debug(f"listing connected lights")

    try:
        for light in manager.selected_lights():
            typer.secho(f"{manager.lights.index(light):3d} ", nl=False, fg="red")
            typer.secho(light.name, fg="green")
            if not verbose:
                continue
            for k, v in light.hidinfo.items():
                if v:
                    typer.secho(f"   {k:>20s}:", nl=False)
                    if isinstance(v, int):
                        typer.secho(f"{v:04x}", fg="blue")
                        continue
                    if isinstance(v, bytes):
                        typer.secho(v.decode("utf-8"), fg="red")
                        continue
                    typer.secho(v, fg="green")
    except NoLightsFound as error:
        typer.secho(f"No lights detected.", fg="red")
        raise typer.Exit(code=-1) from None


@cli.command(name="supported")
def list_supported_lights() -> None:
    """List supported lights."""
    logger.debug("listing supported lights")
    for vendor, names in USBLight.supported_lights().items():
        typer.secho(vendor, fg="blue")
        for name in names:
            typer.secho("  - ", nl=False)
            typer.secho(name, fg="green")


@cli.command(name="udev-rules")
def generate_udev_rules(
    output: typer.FileTextWrite = typer.Option("-", "--output", "-o"),
) -> None:
    """Generate Linux udev rules for all supported lights.

    The rule file generated by this subcommand includes rules for all
    known supported devices. By default, these devices' file permissions
    are set to 0666 when detected by the udev subsystem. Users are
    encouraged to tailor these rules to suit their security needs.
    """

    logger.debug(f"generating udev rules: {output}")

    rules = USBLight.udev_rules()
    about = [
        "# Generated by `busylight udev-rules` https://github.com/JnyJny/busylight",
        "#",
    ]

    print("\n".join(about + rules), file=output)


@webapi.command()
def serve_http_api(
    debug: bool = typer.Option(False, "--debug", "-D", is_flag=True),
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host name to bind the server to.",
    ),
    port: int = typer.Option(
        21169,
        "--port",
        "-p",
        help="Network port number to listen on.",
    ),
) -> None:
    """Serve a HTTP API to access available lights."""

    (logger.enable if debug else logger.disable)("busylight")
    logger.debug("serving http api")

    try:
        import uvicorn
    except ImportError as error:
        logger.error(f"import uvicorn failed: {error}")
        typer.secho(
            "The package `uvicorn` is missing, unabme to serve the busylight API.",
            fg="red",
        )
        raise typer.Exit(code=-1) from None

    try:
        uvicorn.run("busylight.api:busylightapi", host=host, port=port, reload=debug)
    except ModuleNotFoundError as error:
        logger.error(f"Failed to start webapi: {error}")
        typer.secho(
            "Failed to start the webapi.",
            fg="red",
        )
        raise typer.Exit(code=-1) from None


if __name__ == "__main__":
    exit(cli())

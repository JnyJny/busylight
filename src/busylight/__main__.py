"""Busylight command-line interface"""

from dataclasses import dataclass, field
from os import environ
from typing import List, Optional, Tuple

import typer
from busylight_core import Light, NoLightsFoundError
from loguru import logger

from . import __version__
from .color import ColorLookupError, parse_color_string
from .effects import Effects
from .manager import LightManager
from .speed import Speed

cli = typer.Typer()

webcli = typer.Typer()


@dataclass
class GlobalOptions:
    timeout: float = None
    dim: float = 0
    lights: List[int] = field(default_factory=list)
    debug: bool = False


manager = LightManager()


def string_to_scaled_color(ctx: typer.Context, value: str) -> Tuple[int, int, int]:
    """typer.Option callback: translates a string to a Tuple[int, int, int].

    This callback is intended to be used by subcommands after the
    global callback has initialized ctx.obj to an instance of
    GlobalOptions.

    :param ctx: typer.Context
    :param value: str
    :return: Tuple[int, int, int]
    """
    try:
        return parse_color_string(value, ctx.obj.dim)
    except ColorLookupError:
        typer.secho(f"No color match for '{value}'", fg="red")
        raise typer.Exit(code=1) from None


def report_version(value: bool) -> None:
    """typer.Option callback: prints the version string and exits."""
    if value:
        typer.secho(__version__, fg="blue")
        raise typer.Exit()


@cli.callback(invoke_without_command=True, no_args_is_help=True)
def precommand_callback(
    ctx: typer.Context,
    debug: bool = typer.Option(
        False,
        "--debug",
        "-D",
        help="Enable debugging output.",
    ),
    targets: str = typer.Option(
        None,
        "--light-id",
        "-l",
        help="Specify a light or lights to act on.",
    ),
    all_lights: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Use all connected lights.",
    ),
    dim: int = typer.Option(
        100,
        "--dim",
        "-d",
        min=0,
        max=100,
        clamp=True,
        help="Scale color intensity by percentage.",
    ),
    timeout: float = typer.Option(
        None,
        "--timeout",
        show_default=True,
        help="Time out command in seconds.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        is_eager=True,
        callback=report_version,
    ),
) -> None:
    """Control USB connected presense lights."""
    (logger.enable if debug else logger.disable)("busylight")

    options = ctx.ensure_object(GlobalOptions)

    options.debug = debug
    options.dim = dim / 100
    options.timeout = timeout
    options.lights = []

    if ctx.invoked_subcommand == "list" and targets is None:
        all_lights = True

    options.lights.extend(LightManager.parse_target_lights(targets))

    if all_lights:
        options.lights.clear()

    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit(code=1)

    logger.info(f"version {__version__}")
    logger.info(f"timeout={options.timeout}")
    logger.info(f"    dim={options.dim}")
    logger.info(f" lights={options.lights}")
    logger.info(f"    cmd={ctx.invoked_subcommand!r}")


@cli.command(name="on")
def turn_lights_on(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument(
        "green",
        callback=string_to_scaled_color,
        show_default=True,
    ),
) -> None:
    """Activate light."""
    logger.info("activating lights")
    try:
        manager.on(color, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("No lights to turn on.", fg="red")
        raise typer.Exit() from None


@cli.command(name="off")
def turn_lights_off(ctx: typer.Context) -> None:
    """Turn off light."""
    logger.info("deactivating lights")
    try:
        manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("No lights to turn off.", fg="red")


@cli.command(name="blink")
def blink_lights(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument(
        "red",
        callback=string_to_scaled_color,
        show_default=True,
    ),
    speed: Speed = typer.Argument(
        Speed.Slow,
        show_default=True,
    ),
    count: int = typer.Argument(
        0,
        show_default="no limit",
    ),
) -> None:
    """Blink light on and off."""
    logger.info("blinking lights")

    blink = Effects.for_name("blink")(color, speed.duty_cycle, count=count)

    try:
        manager.apply_effect(blink, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("Unable to blink lights.", fg="red")
        raise typer.Exit(code=1) from None


@cli.command(name="rainbow")
def rainbow_lights(
    ctx: typer.Context,
    speed: Speed = typer.Argument(
        Speed.Slow,
        show_default=True,
    ),
    count: int = typer.Argument(
        0,
        show_default="no limit",
    ),
) -> None:
    """Display rainbow colors on specified lights."""
    logger.info("applying rainbow effect")
    rainbow = Effects.for_name("spectrum")(
        speed.duty_cycle / 4,
        scale=ctx.obj.dim,
        count=count,
    )

    try:
        manager.apply_effect(rainbow, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("No rainbow for you.", fg="red")
        raise typer.Exit(code=1) from None


@cli.command(name="pulse")
def pulse_lights(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument(
        "red",
        callback=string_to_scaled_color,
        show_default=True,
    ),
    speed: Speed = typer.Argument(
        Speed.Slow,
        show_default=True,
    ),
    count: int = typer.Argument(
        0,
        show_default="no limit",
    ),
) -> None:
    """Pulse light on and off."""
    logger.info("applying gradient effect")
    throb = Effects.for_name("gradient")(color, speed.duty_cycle / 16, 8, count=count)
    try:
        manager.apply_effect(throb, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("Unable to pulse lights.", fg="red")
        raise typer.Exit(code=1) from None


@cli.command(name="fli")
def flash_lights_impressively(
    ctx: typer.Context,
    color_a: Optional[str] = typer.Argument(
        "red",
        callback=string_to_scaled_color,
        show_default=True,
    ),
    color_b: Optional[str] = typer.Argument(
        "blue",
        callback=string_to_scaled_color,
        show_default=True,
    ),
    speed: Speed = typer.Argument(
        Speed.Slow,
        show_default=True,
    ),
    count: int = typer.Argument(
        0,
        show_default="no limit",
    ),
) -> None:
    """Flash lights impressively between two colors."""
    logger.info("applying fli effect")

    fli = Effects.for_name("blink")(
        color_a,
        speed.duty_cycle / 10,
        off_color=color_b,
        count=count,
    )

    try:
        manager.apply_effect(fli, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("Unable to flash lights impressively.", fg="red")
        raise typer.Exit(code=1) from None


@cli.command(name="list")
def list_available_lights(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Shows additional information about each light.",
    ),
) -> None:
    """List currently connected lights."""
    logger.info("listing connected lights")

    try:
        for light in manager.selected_lights(ctx.obj.lights):
            typer.secho(f"{manager.lights.index(light):3d} ", nl=False, fg="red")
            typer.secho(light.name, fg="green")
            if verbose:
                for key, value in light.hardware.__dict__.items():
                    if key == "handle":
                        continue
                    typer.secho(f"    {key}: ", nl=False, fg="black")
                    typer.secho(f"{value}", fg="blue")

    except NoLightsFoundError:
        typer.secho("No lights detected.", fg="red")
        raise typer.Exit(code=1) from None


@cli.command(name="supported")
def list_supported_lights(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print vendor and product identifiers.",
    ),
) -> None:
    """List supported lights."""
    logger.info("listing supported lights")

    if not verbose:
        for vendor, names in Light.supported_lights().items():
            typer.secho(vendor, fg="blue")
            for name in names:
                typer.secho("  - ", nl=False)
                typer.secho(name, fg="green")
        raise typer.Exit()

    supported_lights = {}
    for subclass in Light.subclasses():
        supported_lights.setdefault(subclass.vendor(), []).append(subclass)

    for vendor, subclasses in supported_lights.items():
        for subclass in subclasses:
            if subclass.supported_device_ids is None:
                continue
            typer.secho(subclass.vendor(), fg="blue")
            for (vid, pid), name in subclass.supported_device_ids.items():
                typer.secho("  - ", nl=False)
                typer.secho(f"0x{vid:04x}:0x{pid:04x} ", fg="red", nl=False)
                typer.secho(name, fg="green")


@cli.command(name="udev-rules")
def generate_udev_rules(
    output: typer.FileTextWrite = typer.Option("-", "--output", "-o"),
) -> None:
    """Generate Linux udev rules for all supported lights.

    The rule file generated by this subcommand includes rules for all
    known supported devices. By default, these device file permissions
    are set to 0666 (ugw=rw-) when detected by the udev subsystem.
    Users are encouraged to tailor these rules to suit their security
    needs.
    """
    logger.info(f"generating udev rules: {output}")

    rules = Light.udev_rules()
    about = [
        "# Generated by `busylight udev-rules` https://github.com/JnyJny/busylight",
        "#",
    ]

    print("\n".join(about + rules), file=output)


@webcli.command()
def serve_http_api(
    debug: bool = typer.Option(False, "--debug", "-D"),
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host name to bind the server to.",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Network port number to listen on.",
    ),
) -> None:
    """Serve a HTTP API to access available lights."""
    environ["BUSYLIGHT_DEBUG"] = str(debug)

    (logger.enable if debug else logger.disable)("busylight")
    logger.info("serving http api")

    try:
        import uvicorn
    except ImportError as error:
        logger.error(f"import uvicorn failed: {error}")
        typer.secho(
            "The package `uvicorn` is missing, unable to serve the busylight API.",
            fg="red",
        )
        raise typer.Exit(code=1) from None

    try:
        uvicorn.run("busylight.api:busylightapi", host=host, port=port, reload=debug)
    except ModuleNotFoundError as error:
        logger.error(f"Failed to start webapi: {error}")
        typer.secho(
            "Failed to start the webapi.",
            fg="red",
        )
        raise typer.Exit(code=1) from None


if __name__ == "__main__":
    exit(cli())

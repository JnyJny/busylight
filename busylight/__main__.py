"""Control USB attached LED lights like a Human™
"""

from pathlib import Path
from sys import stdout
from typing import Tuple, Union, List

import typer

from .manager import LightManager, BlinkSpeed
from .manager import LightIdRangeError, ColorLookupError
from .manager import ALL_LIGHTS

from .lights import USBLight


cli = typer.Typer()


@cli.callback(invoke_without_command=False)
def main_callback(
    ctx: typer.Context,
    light_id: int = typer.Option(
        0,
        "--light-id",
        "-l",
        show_default=True,
        help="Which light to operate on, see list output.",
    ),
    all_lights: bool = typer.Option(
        False, "--all", "-a", is_flag=True, help="Operate on all lights."
    ),
):
    """Control USB attached LED lights like a Human™

    Make a USB attached LED light turn on, off and blink; all from the
    comfort of your very own command-line. If your platform supports
    HIDAPI (Linux, MacOS, Windows and probably others), then you can use
    busylight with supported lights!
    """

    ctx.obj = ALL_LIGHTS if all_lights else light_id


@cli.command(name="list")
def list_subcommand(
    ctx: typer.Context,
    detail: bool = typer.Option(
        False,
        "--long",
        "-l",
        is_flag=True,
        help="Display more information about each light.",
    ),
):
    """List available lights (currently connected)."""

    available = LightManager.available()

    if not available:
        typer.secho("No lights found.", fg="red")
        raise typer.Exit(-1)

    typer.secho("ID: Device Name", fg="blue")
    for index, light in enumerate(available):
        typer.secho(f"{index:2d}", fg="red", nl=False)
        typer.secho(": ", nl=False)
        try:
            product = str(light.info["product_string"]).title()
            typer.secho(f"{product}", fg="green")
        except KeyError:
            typer.secho(f"Product String missing from HID data.", fg="red")
        if detail:
            for key, value in light.info.items():
                typer.secho(f"\t{index:2d}", fg="red", nl=False)
                typer.secho(": ", nl=False)
                typer.secho(f"{key!s}", fg="blue", nl=False)
                typer.secho(": ", nl=False)
                try:
                    typer.secho(f"0x{int(value):02x}", fg="green")
                except ValueError:
                    typer.secho(f"{value!s}", fg="green")


@cli.command(name="on")
def on_subcommand(
    ctx: typer.Context,
    color: str = typer.Argument("green"),
):
    """Turn selected lights on.

    The light selected is turned on with the specified color. The
    default color is green if the user does not supply the color
    argument. Colors can be specified with color names and hexadecimal
    values. Both '0x' and '#' are recognized as hexadecimal number
    prefixes and hexadecimal values may be either three or six digits
    long.

    Examples:

    \b
    ```
    $ busylight on          # light activated with the color green
    $ busylight on red      # now it's red
    $ busylight on 0x00f    # now it's blue
    $ busylight on #ffffff  # now it's white
    $ busylight --all on    # now all available lights are green
    ```
    """

    light_id = ctx.obj

    manager = LightManager()

    try:
        with manager.operate_on(light_id):
            manager.light_on(light_id, color)
    except (LightIdRangeError, ColorLookupError) as error:
        typer.secho(str(error), fg="red")
        raise typer.Exit(-1) from None


# EJO FEATURE list valid color names?


@cli.command(name="off")
def off_subcommand(
    ctx: typer.Context,
):
    """Turn selected lights off.

    Examples:

    \b
    ```
    $ busylight off         # turn off light zero
    $ busylight -l 0 off    # also turns off light zero
    $ busylight --all off   # turns off all connected lights
    ```
    """

    light_id = ctx.obj

    manager = LightManager()
    try:
        with manager.operate_on(light_id, wait_on_animation=False):
            manager.light_off(light_id)
    except LightIdRangeError as error:
        typer.secho(str(error), fg="red")
        raise typer.Exit(-1) from None


@cli.command(name="blink")
def blink_subcommand(
    ctx: typer.Context,
    color: str = typer.Argument("red"),
    speed: BlinkSpeed = typer.Argument(BlinkSpeed.SLOW),
):
    """Activate the selected light in blink mode.

    The light selected will blink with the specified color. The default
    color is red if the user does not supply the color argument. Colors
    can be specified with color names and hexadecimal values. Both '0x'
    and '#' are recognized as hexidecimal number prefixes and
    hexadecimal values may be either three or six digits long.

    Note: Ironically, BlinkStick products cannot be configured to blink
          on and off without software constantly updating the
          devices. If you need your BlinkStick to blink, you will need
          to use the `busylight serve` web API.

    Examples:

    \b
    ```
    $ busylight blink          # light is blinking with the color red
    $ busylight blink green    # now it's blinking green
    $ busylight blink 0x00f    # now it's blinking blue
    $ busylight blink #ffffff  # now it's blinking white
    $ busylight --all blink    # now all available lights are blinking red
    $ busylight --all off      # that's enough of that!
    ```
    """
    light_id = ctx.obj

    manager = LightManager()
    try:
        with manager.operate_on(light_id):
            manager.light_blink(light_id, color, speed)
    except (LightIdRangeError, ColorLookupError) as error:
        typer.secho(str(error), fg="red")
        raise typer.Exit(-1) from None


@cli.command(name="supported")
def supported_subcommand(ctx: typer.Context):
    """List supported LED lights."""

    manager = LightManager()
    with manager.operate_on(None):
        for supported_light in manager.supported:
            typer.secho(supported_light, fg="green")


@cli.command(name="udev-rules")
def udev_rules_subcommand(
    filename: Path = typer.Option(
        None, "--output", "-o", help="Save udev rules to this file."
    )
):
    """Generate a Linux udev rules file.

    Linux uses the udev subsystem to manage USB devices as they are
    plugged and unplugged. By default, only the root user has read and
    write access. The rules generated grant read/write access to all users
    for all known USB lights by vendor id. Modify the rules to suit your
    particular environment.

    Example:

    \b
    ```
    $ busylight udev-rules -o 99-busylight.rules
    $ sudo cp 99-busylight.rules /etc/udev/rules.d
    $ sudo udevadm control -R
    # unplug/plug USB devices
    ```
    """

    # EJO FEATURE mode that only emits rules for lights actually present?

    output = filename.open("w") if filename else stdout

    for supported_light in USBLight.supported_lights():
        for vendor_id in supported_light.vendor_ids():
            print(
                f'KERNEL=="hidraw*", ATTRS{{idVendor}}=="{vendor_id:04x}", MODE="0666"',
                file=output,
            )
            print(
                f'SUBSYSTEM=="usb", ATTRS{{idVendor}}=="{vendor_id:04x}", MODE="0666"',
                file=output,
            )


@cli.command(name="serve")
def serve_subcommand(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-H",
        show_default=True,
        help="Hostname to bind the server to.",
    ),
    port: int = typer.Option(
        8888, "--port", "-p", show_default=True, help="Network port number to listen on"
    ),
):
    """Start a FastAPI-based service to access lights.

    All connected lights are managed by the service, allowing
    long-running animations and effects that the native device APIs
    might not support.

    Once the service is started, the API documentation is available
    via these two URLs:

    \b
    ```
    - `http://<hostname>:<port>/docs`
    - `http://<hostname>:<port>/redoc`
    ```

    Examples:

    \b
    ```
    $ busylight server >& log &
    $ curl http://localhost:8888/1/lights
    $ curl http://localhost:8888/1/lights/on
    $ curl http://localhost:8888/1/lights/off
    $ curl http://localhost:8888/1/light/0/on/purple
    $ curl http://localhost:8888/1/light/0/off
    $ curl http://localhost:8888/1/lights/on
    $ curl http://localhost:8888/1/lights/off
    ```
    """

    try:
        import uvicorn
    except ImportError:
        typer.secho(
            "The package 'uvicorn' is  missing, unable to serve the busylight API.",
            fg="red",
        )
        raise typer.Exit(-1) from None

    try:
        uvicorn.run("busylight.api:server", host=host, port=port)
    except ModuleNotFoundError:
        typer.secho(
            "The package `fastapi` is missing, unable to serve the busylight API",
            fg="red",
        )
        raise typer.Exit(-1) from None

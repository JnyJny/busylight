"""Control USB attached LED lights like a Human™
"""


from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from sys import stdout, stderr
from typing import Tuple, Union, List

import typer

from .manager import LightManager, BlinkSpeed
from .manager import LightIdRangeError, ColorLookupError

from .lights import KNOWN_VENDOR_IDS


cli = typer.Typer()


@cli.callback(invoke_without_command=True)
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

    ![Five Lights at Once](https://github.com/JnyJny/busylight/raw/master/demo/demo.gif)

    Make a supported USB attached LED light turn on, off and blink; all
    from the comfort of your very own command-line. If your platform
    supports HIDAPI (Linux, MacOS, Windows and probably others), then
    you can use `busylight`!

    ## Usage

    \b
    ```console
    $ busylight on
    $ busylight off
    $ busylight on purple
    $ busylight on 0xff00ff   # still purple.
    $ busylight blink yellow  # all hands man your stations.
    $ busylight blink red     # RED ALERT!
    $ busylight off           # all clear.
    ```

    ## Supported Lights
    
    \b
    ```console
    $ busylight supported
    Agile Innovations BlinkStick
    Embrava Blynclight
    ThingM Blink1
    Kuando BusyLight
    Luxafor Flag
    ```

    ## Install
    
    \b
    ```console
    $ pip install -U busylight-for-humans
    $ busylight --help
    ```

    ## Source

    \b
    [busylight](https://github.com/JnyJny/busylight.git)
    """

    ctx.obj = -1 if all_lights else light_id

    #    if not ctx.invoked_subcommand:
    #        ctx.invoke(list_subcommand, ctx)
    #        raise typer.Exit()

    if ctx.invoked_subcommand not in ["supported", "udev-rules"]:
        pass


@cli.command(name="list")
def list_subcommand(
    ctx: typer.Context,
    detail: bool = typer.Option(False, "--long", "-l", is_flag=True),
):
    """List available lights (currently connected).
    """

    available = LightManager.available()

    if not available:
        typer.secho("No lights found.", fg="red")
        raise typer.Exit(-1)

    typer.secho("ID: Device Name", fg="blue")
    for index, light in enumerate(available):
        typer.secho(f"{index:2d}", fg="red", nl=False)
        typer.secho(": ", nl=False)
        typer.secho(f"{light['product_string'].title()}", fg="green")
        if detail:
            for key, value in light.items():
                typer.secho(f"\t{index:2d}", fg="red", nl=False)
                typer.secho(": ", nl=False)
                typer.secho(f"{key!s}", fg="blue", nl=False)
                typer.secho(": ", nl=False)
                try:
                    typer.secho(f"0x{int(value):02x}", fg="green")
                except ValueError:
                    typer.secho(f"{value!s}", fg="green")


@cli.command(name="on")
def on_subcommand(ctx: typer.Context, color: str = typer.Argument("green")):
    """Turn selected lights on.

    The light selected is turned on with the specified color. The default color is green
    if the user omits the color argument. Colors can be specified with color names and
    hexadecimal values. Both '0x' and '#' are recognized as hexidecimal number prefixes
    and hexadecimal values may be either three or six digits long. 

    Examples:

    \b
    ```console
    $ busylight on          # light activated with the color green
    $ busylight on red      # now it's red
    $ busylight on 0x00f    # now it's blue
    $ busylight on #ffffff  # now it's white
    $ busylight --all on    # now all available lights are green
    ```
    
    """

    light_id = ctx.obj

    try:
        with LightManager().operate_on(light_id) as manager:
            manager.light_on(light_id, color)
    except (LightIdRangeError, ColorLookupError) as error:
        typer.secho(str(error), fg="red")
        raise typer.Exit(-1) from None


@cli.command(name="off")
def off_subcommand(ctx: typer.Context,):
    """Turn selected lights off.

    To turn off all lights, specify --all:

    ```console
    $ busylight --all off
    ```

    """
    light_id = ctx.obj

    try:
        with LightManager().operate_on(light_id) as manager:
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

    The light selected will blink with the specified color. The default color is red
    if the user omits the color argument. Colors can be specified with color names and
    hexadecimal values. Both '0x' and '#' are recognized as hexidecimal number prefixes
    and hexadecimal values may be either three or six digits long.

    Note: Ironically, BlinkStick products cannot be configured to blink on and off
          without software constantly updating the devices. If you need your BlinkStick
          to blink, you will need to use the `busylight serve` web API.

    Examples:

    ```console
    $ busylight blink          # light is blinking with the color red
    $ busylight blink green    # now it's blinking green
    $ busylight blink 0x00f    # now it's blinking blue
    $ busylight blink #ffffff  # now it's blinking white
    $ busylight --all blink    # now all available lights are blinking red
    $ busylight --all off      # that's enough of that!
    ```
    """
    light_id = ctx.obj

    try:
        with LightManager().operate_on(light_id) as manager:
            manager.light_blink(light_id, color, speed)
    except (LightIdRangeError, ColorLookupError) as error:
        typer.secho(str(error), fg="red")
        raise typer.Exit(-1) from None


@cli.command(name="supported")
def supported_subcommand(ctx: typer.Context):
    """List supported LED lights.
    """
    with LightManager().operate_on(None) as manager:
        for supported_light in manager.supported:
            typer.secho(supported_light, fg="green")


@cli.command(name="udev-rules")
def udev_rules_subcommand(
    filename: Path = typer.Option(
        None, "--output", "-o", help="Save rules to this file."
    )
):
    """Generate a Linux udev rules file.

    Linux uses the udev subsystem to manage USB devices as they are
    plugged and unplugged. By default, only the root user has read and
    write access. The rules generated grant read/write access to all users
    for all known USB lights by vendor id. Modify the rules to suit your
    particular environment.

    ### Example
    
    \b
    ```console
    $ busylight udev-rules -o 99-busylight.rules
    $ sudo cp 99-busylight.rules /etc/udev/rules.d
    ```
    """

    output = filename.open("w") if filename else stdout

    for vendor_id in KNOWN_VENDOR_IDS:
        v = hex(vendor_id)[2:]
        print(f'KERNEL=="hidraw*", ATTRS{{idVendor}}=="{v}", MODE="0666"', file=output)
        print(f'SUBSYSTEM=="usb", ATTRS{{idVendor}}=="{v}", MODE="0666"', file=output)


@cli.command(name="serve")
def serve_subcommand(
    host: str = typer.Option("0.0.0.0", "--host", "-H"),
    port: int = typer.Option(8888, "--port", "-p"),
):
    """Start a FastAPI-based service that provides access to
    all connected lights via HTTP. All connected lights are managed
    by the service, allowing long-running animations and effects that
    the native device APIs might not support.

    Once the service is started, the API documentation is available
    via these two URLs:

    \b
    `http://<hostname>:<port>/docs`
    `http://<hostname>:<port>/redoc`

    ## Examples

    \b
    ```console
    $ busylight server >& log &
    $ curl http://localhost:8888/1/lights
    $ curl http://localhost:8888/1/lights/on
    $ curl http://localhost:8888/1/lights/off
    $ curl http://localhost:8888/1/light/0/on/purple
    $ curl http://localhost:8888/1/light/0/off

    """

    try:
        import uvicorn
    except ImportError:
        typer.secho(
            "The package 'uvicorn' is  missing, unable to serve the busylight API"
        )
        raise typer.Exit(-1)

    uvicorn.run("busylight.api:server", host=host, port=port)

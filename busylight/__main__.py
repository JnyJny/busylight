"""Control USB attached LED lights like a Human™
"""

from typing import Tuple, Union, List

import typer
import webcolors

from .lights import available_lights, get_light, get_all_lights
from .lights import SUPPORTED_LIGHTS

cli = typer.Typer()


@cli.callback()
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

    ![Two Lights at Once](https://github.com/JnyJny/busylight/raw/master/demo/demo.gif)

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
    Embrava BlyncLight
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
    try:
        if all_lights:
            ctx.obj = list(get_all_lights())
        else:
            ctx.obj = [get_light(light_id)]
    except Exception as error:
        typer.secho(str(error), fg="red")
        raise typer.Exit()


@cli.command(name="list")
def list_subcommand(ctx: typer.Context):
    """List available lights (currently connected).
    
    """

    lights = available_lights()

    if not lights:
        typer.secho("No lights found.", fg="red")
        raise typer.Exit(-1)

    typer.secho("ID: Device Name", fg="blue")
    for index, light in enumerate(lights):
        typer.secho(f"{index:2d}", fg="red", nl=False)
        typer.secho(": ", nl=False)
        typer.secho(f"{light['product_string'].title()}", fg="green")


def handle_color(value: str) -> Tuple[int, int, int]:
    """Returns a tuple of RGB integer values decoded from the supplied `value`.
    
    Value can be a hexidecimal string (0xRRGGBB|0xRGB) or a color name. 

    :param value: str
    """

    if value is None:
        return None

    try:
        if value.startswith("0x"):
            return tuple(webcolors.hex_to_rgb("#" + value[2:]))

        if value.startswith("#"):
            return tuple(webcolors.hex_to_rgb(value))

        return tuple(webcolors.name_to_rgb(value))
    except Exception:
        typer.secho(f"Unable to decode color from '{value}'.", fg="red")
        raise typer.Exit(-1)
    return None


@cli.command(name="on")
def on_subcommand(
    ctx: typer.Context, color: str = typer.Argument("green", callback=handle_color,),
):
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

    for light in ctx.obj:
        light.on(color=color)


@cli.command(name="off")
def off_subcommand(ctx: typer.Context,):
    """Turn selected lights off.

    To turn off all lights, specify --all:

    ```console
    $ busylight --all off
    ```

    """

    for light in ctx.obj:
        light.off()


@cli.command(name="blink")
def blink_subcommand(
    ctx: typer.Context,
    color: str = typer.Argument("red", callback=handle_color,),
    speed: int = typer.Option(1, "--speed", "-s", count=True, help="Blink speed"),
):
    """Activate the selected light in blink mode.

    The light selected will blink with the specified color. The default color is red
    if the user omits the color argument. Colors can be specified with color names and
    hexadecimal values. Both '0x' and '#' are recognized as hexidecimal number prefixes
    and hexadecimal values may be either three or six digits long. 

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

    for light in ctx.obj:
        light.blink(color=color, speed=speed)


@cli.command(name="supported")
def supported():
    """List supported LED lights.
    """
    for light in SUPPORTED_LIGHTS:
        typer.secho(f"{light.__vendor__} {light.__name__}", fg="green")

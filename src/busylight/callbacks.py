""" """

import typer

from .color import ColorLookupError, parse_color_string


def string_to_scaled_color(ctx: typer.Context, value: str) -> tuple[int, int, int]:
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

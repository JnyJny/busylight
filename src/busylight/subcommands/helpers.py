"""Helper functions for CLI subcommands.

This module provides utility functions shared across CLI subcommands.
The main purpose is to encapsulate common logic for working with the
Typer context and light controller, reducing code duplication across
the various subcommand modules.
"""

import typer

from ..controller import LightSelection


def get_light_selection(ctx: typer.Context) -> LightSelection:
    """Get a light selection based on the current CLI context.

    :param ctx: Typer context containing global options and controller

    Examines the global options to determine which lights should be selected.
    If specific light indices are specified in the context, selects those lights.
    Otherwise, selects all available lights.

    Example:
        Use in a subcommand::

            def my_command(ctx: typer.Context):
                selection = get_light_selection(ctx)
                selection.turn_on((255, 0, 0))
    """
    return (
        ctx.obj.controller.by_index(*ctx.obj.lights)
        if ctx.obj.lights
        else ctx.obj.controller.all()
    )

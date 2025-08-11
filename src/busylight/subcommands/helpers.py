"""Helper functions for CLI subcommands."""

import typer


def get_light_selection(ctx: typer.Context):
    """Get light selection from context."""
    return (
        ctx.obj.controller.by_index(*ctx.obj.lights) 
        if ctx.obj.lights 
        else ctx.obj.controller.all()
    )
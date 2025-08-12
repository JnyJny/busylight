# CLI Migration to New LightController

This document shows how to migrate CLI commands from the old LightManager to the new LightController.

## Before (Old LightManager)

```python
# src/busylight/subcommands/on.py
@on_cli.command(name="on")
def activate_lights(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument("green", callback=string_to_scaled_color),
) -> None:
    """Activate lights with a color."""
    logger.info("Activating lights with color: {}", color)

    try:
        ctx.obj.manager.on(color, ctx.obj.lights, timeout=ctx.obj.timeout)
    except (KeyboardInterrupt, TimeoutError):
        ctx.obj.manager.off(ctx.obj.lights)
    except NoLightsFoundError:
        typer.secho("No lights found.", fg="red")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error activating lights: {e}", fg="red")
        raise typer.Exit(code=1)
```

## After (New LightController)

```python
# src/busylight/subcommands/on.py  
@on_cli.command(name="on")
def activate_lights(
    ctx: typer.Context,
    color: Optional[str] = typer.Argument("green"),
) -> None:
    """Activate lights with a color."""
    logger.info("Activating lights with color: {}", color)

    try:
        with ctx.obj.controller as controller:
            # Convert light indices to selection
            if ctx.obj.lights:
                selection = controller.by_index(*ctx.obj.lights)
            else:
                selection = controller.all()
            
            # Turn on lights - much cleaner!
            selection.turn_on(color, timeout=ctx.obj.timeout)
            
    except (KeyboardInterrupt, TimeoutError):
        # Automatic cleanup happens in context manager
        pass
    except NoLightsFoundError:
        typer.secho("No lights found.", fg="red")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error activating lights: {e}", fg="red")
        raise typer.Exit(code=1)
```

## Key Improvements

1. **Cleaner selection**: `controller.by_index(*indices)` instead of complex light ID management
2. **Fluent interface**: `selection.turn_on(color, timeout=timeout)` is much more readable
3. **Automatic cleanup**: Context manager handles resource cleanup automatically
4. **Better error handling**: LightController has better built-in error messages
5. **Color parsing**: Handled automatically in the controller, no need for callback

## Other Command Examples

### Blink Command
```python
# Old way:
effect = Effects.for_name("blink")(color, count=count)
ctx.obj.manager.apply_effect(effect, duty_cycle=speed.duty_cycle, light_ids=ctx.obj.lights, timeout=ctx.obj.timeout)

# New way:
controller.all().blink(color, count=count, speed="slow")
```

### Display Command
```python
# Old way:
lights = ctx.obj.manager.selected_lights(ctx.obj.lights)
for index, light in enumerate(lights):
    typer.secho(f"{index:3d} ", nl=False, fg="red")
    typer.secho(light.name, fg="green")

# New way:
selection = controller.by_index(*ctx.obj.lights) if ctx.obj.lights else controller.all()
for index, name in enumerate(selection.names()):
    typer.secho(f"{index:3d} ", nl=False, fg="red")
    typer.secho(name, fg="green")
```

## Global Options Update

```python
# OLD: src/busylight/global_options.py
@dataclass
class GlobalOptions:
    timeout: float = None
    dim: float = 0
    lights: list[int] = field(default_factory=list)
    debug: bool = False
    manager: LightManager = field(default_factory=LightManager)

# NEW: src/busylight/global_options.py
@dataclass
class GlobalOptions:
    timeout: float = None
    dim: float = 0
    lights: list[int] = field(default_factory=list)
    debug: bool = False
    controller: LightController = field(default_factory=LightController)
```

## Migration Benefits

1. **Readability**: Code reads like natural language
2. **Maintainability**: Easier to understand and modify
3. **Testing**: Much easier to test individual components
4. **Error handling**: Better built-in error messages and handling
5. **Resource management**: Automatic cleanup prevents resource leaks
6. **Flexibility**: Easy to add new selection methods and operations
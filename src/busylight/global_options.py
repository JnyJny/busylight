"""Global options and configuration for the busylight CLI application.

This module defines the global configuration object that holds command-line
options and shared state used throughout the busylight application. The
GlobalOptions dataclass is typically populated during CLI initialization
and passed to subcommands via the Typer context object.

Example:
    The options are typically managed by the CLI framework::

        options = GlobalOptions()
        options.debug = True
        options.lights = [0, 1]  # Select first two lights
        options.dim = 0.5        # 50% brightness
"""

from dataclasses import dataclass, field

from .controller import LightController


@dataclass
class GlobalOptions:
    """Global configuration options for busylight CLI operations.

    This dataclass holds the parsed command-line options and shared state
    that is passed between CLI commands. It includes light selection criteria,
    timeout settings, debugging flags, and the main light controller instance.

    :param timeout: Maximum duration for operations in seconds. None for no timeout
    :param dim: Brightness scaling factor from 0.0 to 1.0
    :param lights: List of light indices to operate on. Empty list means all lights
    :param debug: Whether debug logging is enabled
    :param controller: The main light controller instance

    Example:
        Creating options with custom settings::

            options = GlobalOptions(
                timeout=30.0,
                dim=0.75,
                lights=[0, 2],
                debug=True
            )
    """

    timeout: float = None
    dim: float = 0
    lights: list[int] = field(default_factory=list)
    debug: bool = False
    controller: LightController = field(default_factory=LightController)

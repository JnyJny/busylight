"""Busylight Subcommands"""

from .blink import blink_cli
from .display import display_cli
from .fli import fli_cli
from .off import off_cli
from .on import on_cli
from .pulse import pulse_cli
from .rainbow import rainbow_cli
from .udev_rules import udev_rules_cli

subcommands = [
    blink_cli,
    display_cli,
    fli_cli,
    off_cli,
    on_cli,
    pulse_cli,
    rainbow_cli,
    udev_rules_cli,
]

__all__ = [
    "blink_cli",
    "display_cli",
    "fli_cli",
    "off_cli",
    "on_cli",
    "pulse_cli",
    "rainbow_cli",
    "udev_rules_cli",
]

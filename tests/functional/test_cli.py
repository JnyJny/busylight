"""
"""

import pytest

from typer.testing import CliRunner

from busylight.__main__ import cli

runner = CliRunner()

GOOD_COLORS = [
    "",
    "red",
    "green",
    "blue",
    "#ff00ff",
    "#abc",
    "0x00ff00",
    "0xfff",
]

BAD_COLORS = [
    "foo",
    "#f000",
    "0xf000",
]

# EJO need a lightmanager populated with synthetic lights


@pytest.mark.parametrize("args", ["", "-h", "--help"])
def test_cli_help(args) -> None:
    result = runner.invoke(cli, args)
    assert "Usage" in result.stdout


@pytest.mark.parametrize("color", GOOD_COLORS)
def test_cli_on(color) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 on {color}")


@pytest.mark.parametrize("color", BAD_COLORS)
def test_cli_on_unknown_color(color) -> None:
    result = runner.invoke(cli, ["on", color])


@pytest.mark.parametrize("color", GOOD_COLORS)
def test_cli_blink(color) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 blink {color}")


@pytest.mark.parametrize("color", BAD_COLORS)
def test_cli_blink_unknown_color(color) -> None:
    result = runner.invoke(cli, ["blink", color])


def test_cli_off() -> None:
    result = runner.invoke(cli, ["off"])


def test_cli_list() -> None:
    result = runner.invoke(cli, ["list"])


def test_cli_list_no_lights() -> None:
    result = runner.invoke(cli, ["list"])


def test_cli_supported() -> None:
    result = runner.invoke(cli, ["supported"])


def test_cli_udev_rules() -> None:
    result = runner.invoke(cli, ["udev-rules"])


def test_cli_serve() -> None:
    result = runner.invoke(cli, ["serve"])

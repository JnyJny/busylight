"""
"""

import pytest

from typer.testing import CliRunner

from busylight.__main__ import cli
from busylight.lights import USBLight

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

GOOD_SPEEDS = [
    "",
    "slow",
    "medium",
    "fast",
]

BAD_COLORS = [
    "foo",
    "#f000",
    "0xf000",
]

BAD_SPEEDS = [
    "foo",
    "bar",
    "baz",
]

# EJO need a lightmanager populated with synthetic lights


@pytest.mark.parametrize("args", ["", "-h", "--help"])
def test_cli_help(args) -> None:
    result = runner.invoke(cli, args)
    assert "Usage" in result.stdout


@pytest.mark.parametrize("color", GOOD_COLORS)
def test_cli_on(color) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 on {color}")
    assert "No color match for" not in result.stdout


@pytest.mark.parametrize("color", BAD_COLORS)
def test_cli_on_unknown_color(color) -> None:
    result = runner.invoke(cli, ["on", color])
    assert "No color match for" in result.stdout


@pytest.mark.parametrize("color", GOOD_COLORS)
def test_cli_blink(color) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 blink {color}")
    assert "No color match for" not in result.stdout


@pytest.mark.parametrize("speed", GOOD_SPEEDS)
def test_cli_blink_speed(speed) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 blink green {speed}")


@pytest.mark.parametrize("speed", BAD_SPEEDS)
def test_cli_blink_unknown_speed(speed) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 blink green {speed}")
    assert "Error" in result.stdout


@pytest.mark.parametrize("color", BAD_COLORS)
def test_cli_blink_unknown_color(color) -> None:
    result = runner.invoke(cli, ["blink", color])
    assert "No color match for" in result.stdout


def test_cli_throb():
    pass


def test_cli_throb_colors():
    pass


def test_cli_throb_bad_colors():
    pass


def test_cli_fli():
    pass


def test_cli_fli_colors():
    pass


def test_cli_fli_bad_colors():
    pass


def test_cli_rainbow():
    pass


def test_cli_off() -> None:
    result = runner.invoke(cli, ["off"])
    assert len(result.stdout) == 0


def test_cli_list() -> None:
    result = runner.invoke(cli, ["list"])
    assert len(result.stdout.splitlines()) != 0


def test_cli_supported() -> None:
    expected = USBLight.supported_lights()
    result = runner.invoke(cli, ["supported"])

    for vendor, models in expected.items():
        assert vendor in result.stdout
        for model in models:
            assert model in result.stdout


def test_cli_udev_rules() -> None:
    result = runner.invoke(cli, ["udev-rules"])

    for keyword in [
        'KERNEL=="hidraw*"',
        "ATTRS{idVendor}==",
        "ATTRS{idProduct}==",
        'MODE="0666"',
        'SUBSYSTEM=="usb"',
    ]:
        assert keyword in result.stdout


def test_cli_serve() -> None:
    result = runner.invoke(cli, ["serve"])

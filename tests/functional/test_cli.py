"""
"""

import pytest

from typer.testing import CliRunner

from busylight.__main__ import cli
from busylight.__version__ import __version__
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


@pytest.mark.parametrize("args", ["", "-h", "--help", "-D"])
def test_cli_help(args) -> None:
    result = runner.invoke(cli, args)
    assert "Usage" in result.stdout


def test_cli_version() -> None:
    result = runner.invoke(cli, "--version")
    assert __version__ in result.stdout


@pytest.mark.parametrize("color", GOOD_COLORS)
def test_cli_on(color, lights_available) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 on {color}")
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "No color match for" not in result.stdout


@pytest.mark.parametrize("color", BAD_COLORS)
def test_cli_on_unknown_color(color) -> None:
    result = runner.invoke(cli, ["on", color])
    assert "No color match for" in result.stdout


@pytest.mark.parametrize("color", GOOD_COLORS)
def test_cli_blink(color, lights_available) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 blink {color}")
    if lights_available:
        assert "No color match for" not in result.stdout
    else:
        assert "Unable to blink" in result.stdout


@pytest.mark.parametrize("speed", GOOD_SPEEDS)
def test_cli_blink_speed(speed, lights_available) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 blink green {speed}")
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "Unable to blink" in result.stdout


@pytest.mark.parametrize("speed", BAD_SPEEDS)
def test_cli_blink_unknown_speed(speed) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 blink green {speed}")
    assert "Error" in result.stdout


@pytest.mark.parametrize("color", BAD_COLORS)
def test_cli_blink_unknown_color(color) -> None:
    result = runner.invoke(cli, ["blink", color])
    assert "No color match for" in result.stdout


def test_cli_pulse(lights_available) -> None:
    result = runner.invoke(cli, "--timeout 0.1 pulse")
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "Unable to pulse lights" in result.stdout


@pytest.mark.parametrize("color", GOOD_COLORS)
def test_cli_pulse_colors(color, lights_available) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 pulse {color}")
    assert "No color match for" not in result.stdout


@pytest.mark.parametrize("color", BAD_COLORS)
def test_cli_pulse_unknown_colors(color) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 pulse {color}")
    assert "No color match for" in result.stdout


@pytest.mark.parametrize("speed", GOOD_SPEEDS)
def test_cli_pulse_speed(speed, lights_available) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 pulse green {speed}")
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "Unable to pulse lights" in result.stdout


@pytest.mark.parametrize("speed", BAD_SPEEDS)
def test_cli_pulse_speed(speed) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 pulse green {speed}")
    assert "Error" in result.stdout


def test_cli_fli(lights_available) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 fli")
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "Unable to flash lights impressively" in result.stdout


@pytest.mark.parametrize("color", GOOD_COLORS)
def test_cli_fli_one_color(color, lights_available) -> None:

    result = runner.invoke(cli, f"--timeout 0.1 fli {color}")
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "Unable to flash lights impressively" in result.stdout


@pytest.mark.parametrize("color", GOOD_COLORS)
def test_cli_fli_two_colors(color, lights_available) -> None:

    result = runner.invoke(cli, f"--timeout 0.1 fli {color} {color}")
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "Unable to flash lights impressively" in result.stdout


@pytest.mark.parametrize("color", BAD_COLORS)
def test_cli_fli_unknown_color(color) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 fli {color}")
    assert "No color match" in result.stdout


@pytest.mark.parametrize("good_color, bad_color", zip(GOOD_COLORS, BAD_COLORS))
def test_cli_fli_one_unknown_color(good_color, bad_color) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 fli {good_color} {bad_color}")
    expected = f"No color match for '{bad_color}'"
    assert expected in result.stdout

    result = runner.invoke(cli, f"--timeout 0.1 fli {bad_color} {good_color}")
    assert expected in result.stdout


def test_cli_rainbow(lights_available) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 rainbow")
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "No rainbow for you" in result.stdout


@pytest.mark.parametrize("speed", GOOD_SPEEDS)
def test_cli_rainbow_speed(speed, lights_available) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 rainbow {speed}")
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "No rainbow for you" in result.stdout


@pytest.mark.parametrize("speed", BAD_SPEEDS)
def test_cli_rainbow_unknown_speed(speed) -> None:
    result = runner.invoke(cli, f"--timeout 0.1 rainbow {speed}")
    assert "Error" in result.stdout


def test_cli_off(lights_available) -> None:
    result = runner.invoke(cli, ["off"])
    if lights_available:
        assert len(result.stdout) == 0
    else:
        assert "No lights to turn off" in result.stdout


def test_cli_list(lights_available) -> None:
    result = runner.invoke(cli, ["list"])
    if lights_available:
        assert len(result.stdout.splitlines()) != 0
    else:
        assert "No lights detected" in result.stdout


@pytest.mark.parametrize("verbose", ["--verbose", "-v"])
def test_cli_list_verbose(verbose, lights_available) -> None:
    result = runner.invoke(cli, f"list {verbose}")
    if lights_available:
        assert len(result.stdout.splitlines()) != 0
    else:
        assert "No lights detected" in result.stdout


def test_cli_list_specific_light(lights_available) -> None:
    result = runner.invoke(cli, "--light-id 0 list")
    if lights_available:
        assert len(result.stdout.splitlines()) == 1
    else:
        assert "No lights detected" in result.stdout


@pytest.mark.parametrize("verbose", ["--verbose", "-v"])
def test_cli_list_specific_light(verbose, lights_available) -> None:
    result = runner.invoke(cli, f"--light-id 0 list {verbose}")
    if lights_available:
        assert len(result.stdout.splitlines()) > 1
    else:
        assert "No lights detected" in result.stdout


def test_cli_supported() -> None:
    expected = USBLight.supported_lights()
    result = runner.invoke(cli, ["supported"])

    for vendor, models in expected.items():
        assert vendor in result.stdout
        for model in models:
            assert model in result.stdout


def test_cli_udev_rules_contents() -> None:

    supported = USBLight.supported_lights()
    nsupported = sum(len(v) for v in supported.values())

    result = runner.invoke(cli, ["udev-rules"])

    for keyword, count in [
        ('KERNEL=="hidraw*"', nsupported),
        ('SUBSYSTEM=="usb"', nsupported),
        ("ATTRS{idVendor}==", nsupported * 2),
        ("ATTRS{idProduct}==", nsupported * 2),
        ('MODE="0666"', nsupported * 2),
    ]:
        assert result.stdout.count(keyword) == count

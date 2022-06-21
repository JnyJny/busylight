import pytest

from typer.testing import CliRunner

from busylight.__main__ import webcli


runner = CliRunner()


def test_webcli_help() -> None:
    result = runner.invoke(webcli, "--help")
    assert "Usage" in result.stdout


# def test_webcli_start() -> None:
#    result = runner.invoke(webcli)

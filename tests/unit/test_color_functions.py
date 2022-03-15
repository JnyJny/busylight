"""
"""

import pytest

from busylight.lights.color import parse_color


@pytest.mark.parametrize(
    "value,expected",
    [
        ("black", (0, 0, 0)),
        ("Black", (0, 0, 0)),
        ("BlAcK", (0, 0, 0)),
        ("BLACK", (0, 0, 0)),
        ("#000000", (0, 0, 0)),
        ("#000", (0, 0, 0)),
        ("0x000000", (0, 0, 0)),
        ("0x000", (0, 0, 0)),
        ("0X000000", (0, 0, 0)),
        ("0X000", (0, 0, 0)),
    ],
)
def test_parse_color(value, expected) -> None:

    result = parse_color(value)
    assert result == expected


@pytest.mark.parametrize(
    "value",
    [
        "#0",
        "#00",
        "#0000",
        "#00000",
        "#0000000",
        "0x0",
        "0x00",
        "0x0000",
        "0x00000",
        "0x0000000",
        "bogus green",
    ],
)
def test_parse_color_invalid(value) -> None:

    with pytest.raises(ValueError):
        parse_color(value)

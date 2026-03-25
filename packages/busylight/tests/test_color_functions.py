"""Test Color Handling"""

from typing import List, Tuple

import pytest
from busylight.color import (
    ColorLookupError,
    colortuple_to_name,
    parse_color_string,
    scale_color,
)


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
def test_parse_color_string(value: str, expected: Tuple[int, int, int]) -> None:
    result = parse_color_string(value)
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
def test_parse_color_string_invalid(value: str) -> None:
    with pytest.raises(ColorLookupError):
        parse_color_string(value)


@pytest.mark.parametrize(
    "value,expected",
    [
        ((0, 0, 0), "black"),
        ((255, 255, 255), "white"),
        ((255, 0, 0), "red"),
        ((0, 128, 0), "green"),
        ((0, 0, 255), "blue"),
    ],
)
def test_colortuple_to_name(value: Tuple[int, int, int], expected: str) -> None:
    result = colortuple_to_name(value)
    assert result == expected


@pytest.mark.parametrize(
    "color,expected", [((0, 0, 1), "#000001"), ((255, 254, 253), "#fffefd")]
)
def test_colortuple_to_name_unknown_color(
    color: Tuple[int, int, int], expected
) -> None:
    result = colortuple_to_name(color)
    assert result == expected


@pytest.mark.parametrize(
    "source,scale,expected",
    [
        ((255, 255, 255), 1.00, (255, 255, 255)),
        ((255, 255, 255), 2.00, (255, 255, 255)),
        ((255, 255, 255), 0.75, (191, 191, 191)),
        ((255, 255, 255), 0.50, (128, 128, 128)),
        ((255, 255, 255), 0.25, (64, 64, 64)),
        ((255, 255, 255), 0.00, (0, 0, 0)),
        ((255, 255, 255), -1.0, (0, 0, 0)),
        ((0, 0, 0), 1.00, (0, 0, 0)),
        ((0, 0, 0), 0.75, (0, 0, 0)),
        ((0, 0, 0), 0.50, (0, 0, 0)),
        ((0, 0, 0), 0.25, (0, 0, 0)),
        ((0, 0, 0), 0.00, (0, 0, 0)),
    ],
)
def test_scale_color(
    source: Tuple[int, int, int], scale: float, expected: Tuple[int, int, int]
) -> None:
    result = scale_color(source, scale)
    assert result == expected

    result = scale_color(expected)
    assert result == expected

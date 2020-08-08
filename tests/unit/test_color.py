"""Color Tests

Users may specify colors in many different formats:

- 6 digit hexadecimal number with optional #/0x prefix
- 3 digit hexadecimal number with optional #/0x prefix
- English color names

"""

import pytest

from busylight.color import normalize_hex_str, color_to_rgb


@pytest.mark.parametrize(
    "given, expected",
    [
        ("0xaabbcc", "#aabbcc"),
        ("#ddeeff", "#ddeeff"),
        ("0xa1b2c3d4", "#a1b2c3d4"),
        ("0xabc", "#abc"),
        ("#def", "#def"),
        ("cab", "#cab"),
    ],
)
def test_noramlize_hex_string_good(given, expected):

    assert normalize_hex_str(given) == expected
    assert normalize_hex_str(given.upper()) == expected
    assert normalize_hex_str(given.title()) == expected


@pytest.mark.parametrize("given", [None, 0, 0.0, [], {}, ()])
def test_normalize_hex_string_invalid(given):

    with pytest.raises(ValueError):
        result = normalize_hex_str(given)


@pytest.mark.parametrize(
    "given, expected",
    [
        ("#ff0000", (255, 0, 0)),
        ("0x00ff00", (0, 255, 0)),
        ("0000ff", (0, 0, 255)),
        ("white", (255, 255, 255)),
        ("red", (255, 0, 0)),
        ("green", (0, 128, 0)),
        ("blue", (0, 0, 255)),
        ("#f00", (255, 0, 0)),
        ("#0f0", (0, 255, 0)),
        ("#00f", (0, 0, 255)),
        ("0xf00", (255, 0, 0)),
        ("0x0f0", (0, 255, 0)),
        ("0x00f", (0, 0, 255)),
        ("f00", (255, 0, 0)),
        ("0f0", (0, 255, 0)),
        ("00f", (0, 0, 255)),
    ],
)
def test_color_to_rgb_good(given, expected):

    assert color_to_rgb(given) == expected
    assert color_to_rgb(given.upper()) == expected
    assert color_to_rgb(given.title()) == expected


@pytest.mark.parametrize(
    "given",
    [
        "0xaabbccdd",
        "#aabbccdd",
        "aabbccdd",
        "0xa",
        "#a",
        "a",
        "0xab",
        "#ab",
        "ab",
        "0xabcd",
        "#abcd",
        "abcd",
        "0xabcde",
        "#abcde",
        "abcde",
        "boguscolorname",
        "0xnothex",
        "#nothex",
        "nothex",
    ],
)
def test_color_to_rgb_invalid(given):

    with pytest.raises(ValueError):
        result = color_to_rgb(given)

    with pytest.raises(ValueError):
        result = color_to_rgb(given.upper())

    with pytest.raises(ValueError):
        result = color_to_rgb(given.title())

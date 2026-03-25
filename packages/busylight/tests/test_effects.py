""" """

import pytest
from busylight.effects import Blink, Effects, Gradient, Spectrum, Steady


def test_effects_classmethod_subclasses():
    subclasses = Effects.subclasses()
    assert isinstance(subclasses, dict)
    for name, subclass in subclasses.items():
        assert name == subclass.__name__.casefold()
        assert issubclass(subclass, Effects)
        result = subclass.subclasses()
        assert isinstance(result, dict)


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Blink", Blink),
        ("blink", Blink),
        ("BLINK", Blink),
        ("bLiNk", Blink),
        ("gradient", Gradient),
        ("spectrum", Spectrum),
        ("steady", Steady),
    ],
)
def test_effects_classmethod_for_name(name, expected) -> None:
    result = Effects.for_name(name)
    assert result == expected


@pytest.mark.parametrize("name", ["foo", "bar", "baz"])
def test_effects_classmethod_for_name_unknown(name) -> None:
    with pytest.raises(ValueError):
        result = Effects.for_name(name)

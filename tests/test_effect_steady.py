""" """

import pytest
from busylight.effects import Steady


@pytest.mark.parametrize(
    "color",
    [
        (255, 255, 255),
    ],
)
def test_effect_steady_init(color) -> None:
    instance = Steady(color)

    assert isinstance(instance, Steady)
    assert instance.name in str(instance)
    assert instance.name in repr(instance)
    assert instance.color == color
    assert instance.duty_cycle == 86400  # one day in seconds
    assert color in instance.colors

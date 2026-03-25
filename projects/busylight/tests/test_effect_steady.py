"""Tests for Steady effect."""

import pytest
from busylight.effects import Steady
from busylight_core.mixins.taskable import TaskPriority


@pytest.mark.parametrize(
    "color",
    [
        (255, 255, 255),
        (128, 64, 32),
        (0, 255, 0),
    ],
)
def test_effect_steady_init(color) -> None:
    instance = Steady(color)

    assert isinstance(instance, Steady)
    assert instance.name in str(instance)
    assert instance.name in repr(instance)
    assert instance.color == color
    assert instance.default_interval == 0.0
    assert instance.priority == TaskPriority.NORMAL
    assert color in instance.colors
    assert len(instance.colors) == 1

"""Tests for Gradient effect."""

import pytest
from busylight.effects import Gradient
from busylight_core.mixins.taskable import TaskPriority


@pytest.mark.parametrize(
    "color,step,count",
    [
        ((255, 255, 255), 1, 0),
        ((255, 255, 255), 1, 1),
        ((128, 64, 32), 5, 2),
    ],
)
def test_effect_gradient_init(color, step, count) -> None:
    instance = Gradient(color, step, count=count)

    repr_result = repr(instance)
    str_result = str(instance)

    assert isinstance(instance, Gradient)
    assert instance.name == "Gradient"
    assert instance.step == step
    assert instance.count == count
    assert instance.default_interval == 0.1
    assert instance.priority == TaskPriority.LOW

    assert instance.name in repr_result
    assert instance.name in str_result
    assert len(instance.colors) > 0
    assert color in instance.colors

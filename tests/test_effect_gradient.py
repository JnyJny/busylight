""" """

import pytest
from busylight.effects import Gradient


@pytest.mark.parametrize(
    "color,duty_cycle,step,count",
    [
        ((255, 255, 255), 0.5, 1, 0),
        ((255, 255, 255), 0.5, 1, 1),
    ],
)
def test_effect_gradient_init(color, duty_cycle, step, count) -> None:
    instance = Gradient(color, duty_cycle, step, count)

    repr_result = repr(instance)
    str_result = str(instance)

    assert isinstance(instance, Gradient)
    assert instance.name == "Gradient"

    assert instance.duty_cycle == duty_cycle
    assert instance.step == step
    assert instance.count == count

    assert instance.name in repr_result
    assert instance.name in str_result

    assert len(instance.colors) != 0

    assert color in instance.colors

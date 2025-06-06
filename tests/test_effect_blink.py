""" """

import pytest
from busylight.effects import Blink


@pytest.mark.parametrize(
    "on_color,duty_cycle,off_color,count",
    [
        ((255, 255, 255), 0.22, None, 3),
        ((128, 255, 32), 0.22, (32, 32, 32), 0),
    ],
)
def test_blink_init(on_color, duty_cycle, off_color, count) -> None:
    instance = Blink(on_color, duty_cycle, off_color, count)

    assert instance.name == "Blink"

    repr_result = repr(instance)
    str_result = str(instance)

    assert isinstance(instance, Blink)
    assert instance.on_color == on_color
    assert instance.duty_cycle == duty_cycle
    assert instance.count == count

    assert on_color in instance.colors
    assert repr(on_color) in repr_result
    assert repr(duty_cycle) in repr_result

    if off_color is None:
        assert instance.off_color == (0, 0, 0)
        assert (0, 0, 0) in instance.colors
        assert repr((0, 0, 0)) in repr_result
    else:
        assert instance.off_color == off_color
        assert off_color in instance.colors
        assert repr(off_color) in repr_result

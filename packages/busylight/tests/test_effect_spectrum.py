"""Tests for Spectrum effect."""

import pytest
from busylight.effects import Spectrum
from busylight_core.mixins.taskable import TaskPriority


@pytest.mark.parametrize(
    "scale,steps,frequency,phase,center,width,count",
    [
        (1.0, 64, None, None, 128, 127, 1),
        (0.5, 32, (0.2, 0.2, 0.2), (0, 2, 4), 64, 63, 0),
    ],
)
def test_spectrum_init(
    scale,
    steps,
    frequency,
    phase,
    center,
    width,
    count,
) -> None:
    instance = Spectrum(scale, steps, frequency, phase, center, width, count)

    assert instance.name == "Spectrum"
    assert isinstance(instance, Spectrum)
    assert instance.scale == scale
    assert instance.steps == steps
    assert instance.count == count
    assert instance.default_interval == 0.05
    assert instance.priority == TaskPriority.LOW

    repr_result = repr(instance)
    str_result = str(instance)

    assert instance.name in repr_result
    assert instance.name in str_result
    assert len(instance.colors) > 0

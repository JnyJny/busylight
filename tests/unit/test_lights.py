"""
"""

import pytest

from busylight.lights import USBLight

from busylight.lights import USBLightNotFound
from busylight.lights import USBLightUnknownVendor
from busylight.lights import USBLightUnknownProduct


def test_supported_light_instance_type(supported_lights):
    """Given a list of USBLight subclasses:
    - test the subclass membership in USBLight
    - call first_light until it returns USBLightNotFound
    - call all_lights and verify it returns a list
    """
    for supported_light in supported_lights:

        assert issubclass(supported_light, USBLight)

        with pytest.raises(USBLightNotFound):
            acquired_lights = []
            while True:
                acquired_lights.append(supported_light.first_light())

        # release any lights captured here
        for light in acquired_lights:
            del light

        results = supported_light.all_lights()
        assert isinstance(results, list)

        # release any lights captured
        for light in results:
            del light


def test_light_instances(lights):
    """"""
    for light in lights:
        assert light and light.is_acquired

        light.on((255, 0, 0))
        assert light.is_on
        light.off()
        assert not light.is_on

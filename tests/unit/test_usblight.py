"""
"""

import pytest

from busylight.lights import USBLight
from busylight.lights import USBLightNotFound


def test_usblight_create_fails():
    """USBLight is an abstract base class which may not be
    instantiated directly.
    """

    with pytest.raises(TypeError, match="abstract methods"):
        u = USBLight(0, 0, b"path", False)


def test_supported_lights():
    """The supported_lights() classmethod returns a list of
    USBLight concrete subclasses.
    """
    supported_lights = USBLight.supported_lights()

    assert isinstance(supported_lights, list)
    for light in supported_lights:
        assert issubclass(light, USBLight)


def test_usblight_first_light():
    """The first_light() classmethod returns a configured
    light or raises USBLightNotFound when no more lights
    can be located.
    """
    with pytest.raises(USBLightNotFound):
        lights = []
        while True:
            lights.append(USBLight.first_light())


def test_usblight_all_lights():

    result = USBLight.all_lights()
    assert isinstance(result, list)


def test_incomplete_usblight_subclass():

    # EJO this test is last since it "pollutes" the USBLight subclasses
    #     with an incomplete instance.

    class incomplete(USBLight):
        pass

    with pytest.raises(TypeError, match="abstract methods"):
        instance = incomplete()

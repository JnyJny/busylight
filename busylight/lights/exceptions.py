""" raised by busylight.lights.light.Light and subclasses
"""


class _BaseLightException(Exception):
    pass


class InvalidLightInfo(_BaseLightException):
    """The dictionary passed to Light.__init__ is missing required key/value pairs."""


class LightUnavailable(_BaseLightException):
    """Previously accessible light is now not accessible."""


class LightUnsupported(_BaseLightException):
    """The dictionary passed to an __init__ method of a subclass of Light
    does not describe a light supported by the subclass."""


class NoLightsFound(_BaseLightException):
    """No lights were discovered by any subclass of Light."""

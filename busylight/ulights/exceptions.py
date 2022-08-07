"""
"""


class BaseLightException(Exception):
    pass


class InvalidLightInfo(BaseLightException):
    pass


class LightNotFound(BaseLightException):
    pass


class LightUnavailable(BaseLightException):
    pass


class LightUnsupported(BaseLightException):
    pass


class NoLightsFound(BaseLightException):
    pass

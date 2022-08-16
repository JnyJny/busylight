"""USBLight Exceptions
"""

from typing import Dict, Union

from loguru import logger


class InvalidHidInfo(Exception):
    """The dictionary from hid.enumerate is somehow broken."""

    def __init__(self, hidinfo: Dict[str, Union[bytes, int, str]]) -> None:
        super().__init__(hidinfo)
        self.hidinfo = hidinfo


class NoLightsFound(Exception):
    """No lights available for use."""


class BaseLightException(Exception):
    @classmethod
    def from_dict(
        cls, hidinfo: Dict[str, Union[bytes, int, str]]
    ) -> "BaseLightException":
        """Convenience method for initializing light exceptions."""
        try:
            return cls(hidinfo["vendor_id"], hidinfo["product_id"], hidinfo["path"])
        except KeyError as error:
            logger.error("BAD hidinfo {error}")
            raise InvalidHidInfo(hidinfo)

    def __init__(self, vendor_id: int, product_id: int, path: bytes = None) -> None:
        """
        :vendor_id: 2-byte integer
        :product_id: 2-byte integer
        :path: optional bytes encoded device path
        """
        super().__init__(vendor_id, product_id, path)
        self.vendor_id: str = f"vendor_id={vendor_id:04x}"
        self.product_id: str = f"product_id={product_id:04x}"
        self.device_id: str = f"{vendor_id:04x}:{product_id:04x}"
        self.path: str = f"path={path!r}"
        self.name: str = self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.name}({self.vendor_id}, {self.product_id}, {self.path})"

    def __str__(self) -> str:
        return f"{self.name}: {self.device_id} {self.path}"


class LightUnavailable(BaseLightException):
    """This light is not available to be opened or conduct I/O."""


class LightNotFound(BaseLightException):
    """A requested light was not found."""


class LightUnsupported(BaseLightException):
    """The requested light is not supported by this subclass."""

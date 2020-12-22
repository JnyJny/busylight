"""USB Light Exceptional Events
"""


class USBLightNotFound(Exception):
    """Requested light was not found."""


class USBLightUnknownVendor(Exception):
    """Requested device vendor_id not supported by this class."""


class USBLightUnknownProduct(Exception):
    """Requested device product_id not supported by this class."""


class USBLightInUse(Exception):
    """Device open failed, already open."""


class USBLightIOError(Exception):
    """Error occurred writing to device."""

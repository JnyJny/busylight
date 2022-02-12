"""USB Light Exceptional Events
"""


class USBLightBaseException(Exception):
    """Base USBLight Exception"""

    def __repr__(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return f"{self.__doc__}"


class USBLightNotFound(USBLightBaseException):
    """Requested light was not found"""


class USBLightUnknownVendor(USBLightBaseException):
    """Requested device vendor_id not supported"""

    def __init__(self, vendor_id: int) -> None:
        self.vendor_id = vendor_id

    def __repr__(self) -> str:
        return f"{super().__repr__()}(vendor_id=0x{self.vendor_id:04x})"

    def __str__(self) -> str:
        return f"{super().__str__()}: vendor_id=0x{self.vendor_id:04x}"


class USBLightUnknownProduct(USBLightBaseException):
    """Requested device product_id not supported"""

    def __init__(self, product_id: int) -> None:
        self.product_id = product_id

    def __repr__(self) -> str:
        return f"{super().__repr__()}(product_id=0x{self.product_id:04x})"

    def __str__(self) -> str:
        return f"{super().__str__()}: product_id=0x{self.product_id:04x}"


class USBLightInUse(USBLightBaseException):
    """Device open failed, already open"""


class USBLightIOError(USBLightBaseException):
    """Error occurred writing to device"""

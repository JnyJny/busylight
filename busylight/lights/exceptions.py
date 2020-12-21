"""
"""


class USBLightNotFound(Exception):
    pass


class USBLightUnknownVendor(Exception):
    pass


class USBLightUnknownProduct(Exception):
    pass


class USBLightInUse(Exception):
    pass


class USBLightIOError(Exception):
    pass

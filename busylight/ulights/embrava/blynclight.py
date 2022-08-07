"""
"""

from ..hidlight import HIDLight, HIDInfo


class Blynclight(HIDLight):

    supported_device_ids = {
        (0x2C0D, 0x0001): "Blynclight",
        (0x2C0D, 0x000A): "Blynclight Mini",
        (0x2C0D, 0x000C): "Blynclight",
        (0x2C0D, 0x0010): "Blynclight Plus",
        (0x0E53, 0x2517): "Blynclight Mini",
        (0x0E53, 0x2516): "Blynclight",
    }

    vendor = "Embrava"

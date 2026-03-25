"""Busy Tag Implementation Details"""

# https://luxafor.helpscoutdocs.com/article/47-busy-tag-usb-cdc-command-reference-guide

from enum import Enum


class Command(str, Enum):
    GetDeviceName: str = "AT+GDN"
    GetManufacturerName: str = "AT+GMN"
    GetDeviceID: str = "AT+GID"
    GetPictureList: str = "AT+GPL"
    GetFileList: str = "AT+GFL"
    GetLocalHostAddress: str = "AT+GLHA"
    GetFreeStorageSize: str = "AT+GFSS"
    GetTotalStorageSize: str = "AT+GTSS"
    GetLastErrorCode: str = "AT+GLEC"
    GetLastResetReasonCore0: str = "AT+GLRR0"
    GetLastResetReasonCore1: str = "AT+GLRR1"
    SolidColor: str = "AT+SC={leds},{red:02x}{green:02x}{blue:02x}"

    @classmethod
    def solid_color(cls, color: tuple[int, int, int], led: int = 0) -> str:
        red, green, blue = color
        led = 0b01111111 if led == 0 else 1 << led

        return cls.SolidColor.format(leds=led, red=red, green=green, blue=blue)

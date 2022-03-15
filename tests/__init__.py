"""
"""

from time import time
from typing import Generator, Union

from loguru import logger


def is_valid_hidinfo(hidinfo: dict[str, Union[bytes, int, str]]) -> None:
    """ """
    return all(
        (
            isinstance(hidinfo, dict),
            "vendor_id" in hidinfo,
            "product_id" in hidinfo,
            "path" in hidinfo,
            all(isinstance(key, str) for key in hidinfo),
            all(isinstance(value, (bytes, int, str)) for value in hidinfo.values()),
        )
    )


def device_hidinfo(subclass) -> Generator[dict, None, None]:

    for (vid, pid), name in subclass.SUPPORTED_DEVICE_IDS.items():
        vpid = f"{vid:04x}:{pid:04x}"
        product_string = f"{vpid} {subclass.__name__.title()}"
        yield {
            "vendor_id": vid,
            "product_id": pid,
            "path": f"bogus/path/{time()}/{vpid}".encode("utf-8"),
            "product_string": product_string,
            "serial_number": "BS032974-3.0",
            "release_number": 0x0200,
            "usage_page": vid + pid,
            "usage": 0,
        }


def device_hidinfo_unknown(subclass) -> Generator[dict, None, None]:

    for item in device_hidinfo(subclass):
        item["vendor_id"] = 0xFFFF
        yield item
        item["product_id"] = 0xFFFF
        yield item

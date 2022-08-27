"""
"""

import pytest

from typing import Dict, List, Union

from busylight.lights import (
    LightUnavailable,
    LightNotFound,
    LightUnsupported,
    NoLightsFound,
    InvalidHidInfo,
)

from busylight.lights.exceptions import BaseLightException


def check_baselightexception(
    error: BaseLightException,
    vendor_id: int,
    product_id: int,
    path: bytes,
) -> bool:

    vendor_id_hex_str = hex(vendor_id)[2:].lower()
    product_id_hex_str = hex(product_id)[2:].lower()

    return all(
        [
            isinstance(error.vendor_id, str),
            vendor_id_hex_str in error.vendor_id,
            isinstance(error.product_id, str),
            product_id_hex_str in error.product_id,
            isinstance(error.path, str),
            repr(path) in error.path,
            isinstance(error.device_id, str),
            vendor_id_hex_str in error.device_id,
            product_id_hex_str in error.device_id,
            isinstance(error.name, str),
            error.name in repr(error),
            vendor_id_hex_str in repr(error),
            product_id_hex_str in repr(error),
            repr(path) in repr(error),
            hasattr(error, "args"),
        ]
    )


@pytest.mark.parametrize(
    "exception_class", [LightUnavailable, LightNotFound, LightUnsupported]
)
def test_exception_baselightexceptions_init(exception_class) -> None:

    vendor_id = 0xDEAD
    product_id = 0xBEEF
    path = b"/fake/device/path"

    error = exception_class(vendor_id, product_id, path)

    assert check_baselightexception(error, vendor_id, product_id, path)

    with pytest.raises(exception_class):
        raise error


@pytest.mark.parametrize(
    "exception_class", [LightUnavailable, LightNotFound, LightUnsupported]
)
def test_exception_baselightexceptions_with_good_hidinfo(
    exception_class, hidinfo_list
) -> None:

    # EJO No reason to iterate thru all the hidinfo buckets in the list,
    #     if it works for one it will work for all.

    for hidinfo in hidinfo_list[:1]:
        error = exception_class.from_dict(hidinfo)
        assert check_baselightexception(
            error,
            hidinfo["vendor_id"],
            hidinfo["product_id"],
            hidinfo["path"],
        )

        with pytest.raises(exception_class):
            raise error


@pytest.mark.parametrize(
    "exception_class", [LightUnavailable, LightNotFound, LightUnsupported]
)
def test_exception_baselightexceptions_with_broken_hidinfo(
    exception_class, broken_hidinfo_list
) -> None:

    for hidinfo in broken_hidinfo_list[:1]:
        with pytest.raises(InvalidHidInfo):
            error = exception_class.from_dict(hidinfo)


def test_exception_nolightsfound() -> None:

    error = NoLightsFound()
    with pytest.raises(NoLightsFound):
        raise error


def test_exception_invalidhidinfo_with_good_hidinfo(hidinfo_list) -> None:

    for hidinfo in hidinfo_list[:1]:
        error = InvalidHidInfo(hidinfo)
        assert hasattr(error, "args")
        assert hasattr(error, "hidinfo")
        assert error.hidinfo == hidinfo
        with pytest.raises(InvalidHidInfo):
            raise error


def test_exception_invalidhidinfo_with_broken_hidinfo(broken_hidinfo_list) -> None:

    for hidinfo in broken_hidinfo_list[:1]:
        error = InvalidHidInfo(hidinfo)
        assert hasattr(error, "args")
        assert hasattr(error, "hidinfo")
        assert error.hidinfo == hidinfo
        with pytest.raises(InvalidHidInfo):
            raise error

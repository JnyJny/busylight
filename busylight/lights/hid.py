"""
"""

from typing import Dict, List

import hid


# Why This File Exists.
#
# The 'apmorton/pyhidapi' package and 'trezor/cython-hidapi' packages both
# occupy the 'hid' namespace when installed. Regardless of install order,
# apmorton/pyhidapi wins and overwrites cython-hidapi in the directory
# */lib/python3*/site-packages/hid. The two packages provide similar
# support for performing IO to USB human interface devices.  Similar but
# not the same.
#
# I picked the trezor/cython-hidapi package for HID support because it
# does not require the user to install additional non-Python software.
# The pyhidapi package is a ctypes interface to the hidapi shared object
# which the user must install in an operation separate from the `pip
# install`.
#
# Both hid and hidapi support a function `enumerate` which returns a
# list of dictionaries, each dictionary describing discovered USB
# devices.
#
# The Device class wallpapers over the differences between hid.device
# and hid.Device, favoring the open semantics of hid.device since it
# requires fewer changes to the caller.


def enumerate() -> List[Dict]:
    return hid.enumerate()


class Device:
    def __init__(self) -> None:
        try:
            self._handle = hid.device()
        except AttributeError:
            self._handle = None

    def open(
        self,
        vendor_id: int,
        product_id: int,
        serial_number: str = None,
    ) -> None:
        """Open the first device matching vendor_id and product_id or serial number."""
        if self._handle:
            self._handle.open(vendor_id, product_id, serial_number)
        else:
            self._handle = hid.Device(
                vid=vendor_id, pid=product_id, serial=serial_number
            )

    def open_path(self, path: bytes) -> None:
        """Open the device at path."""
        if self._handle:
            self._handle.open_path(path)
        else:
            self._handle = hid.Device(path=path)

    def close(self) -> None:
        """Close the device."""
        try:
            self._handle.close()
        except AttributeError:
            raise IOError("device not open") from None

    def read(self, nbytes: int, timeout_ms: int = None) -> List[int]:
        """Read nbytes from the device, returns a list of ints."""
        try:
            return self._handle.read(nbytes, timeout_ms)
        except AttributeError:
            raise IOError("device not open") from None

    def write(self, buf: bytes) -> int:
        """Write bytes in buf to the device."""
        try:
            return self._handle.write(buf)
        except AttributeError:
            raise IOError("device not open") from None

    def get_feature_report(self, report: int, nbytes: int) -> List[int]:
        """Read a nbytes feature report from the device."""
        try:
            return self._handle.get_feature_report(report, nbytes)
        except AttributeError:
            raise IOError("device not open") from None

    def send_feature_report(self, buf: bytes) -> int:
        """Write bytes in buf as a device feature report."""
        try:
            return self._handle.send_feature_report(buf)
        except AttributeError:
            raise IOError("device not open") from None

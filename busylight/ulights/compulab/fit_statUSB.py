"""
"""

from loguru import logger

from ..seriallight import SerialLight, SerialInfo


class Fit_StatUSB(SerialLight):

    supported_device_ids = {
        (0, 0): "fit-statUSB",
    }

    vendor = "Compulab"

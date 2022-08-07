"""
"""

from loguru import logger

from ..seriallight import SerialLight


class MuteSync(SerialLight):

    supported_device_ids = {}

    vendor = "MuteSync"

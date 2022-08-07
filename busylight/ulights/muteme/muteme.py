"""
"""

from loguru import logger

from ..hidlight import HIDLight, HIDInfo


class MuteMe(HIDLight):

    supported_device_ids = {}

    vendor = "MuteMe"

"""Control USB Attached Lights with Style!"""

from importlib.metadata import distribution

from loguru import logger

__version__ = distribution("busylight-for-humans").version

logger.disable("busylight")

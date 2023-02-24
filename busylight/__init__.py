"""Control USB Attached Lights with Style!

"""

try:
    from importlib.metadata import distribution
except ModuleNotFoundError:
    from importlib_metadata import distribution

from loguru import logger

__version__ = distribution("busylight-for-humans").version

logger.disable("busylight")

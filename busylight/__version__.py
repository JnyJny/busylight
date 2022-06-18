""" Busylight version machinery.
"""

from pkg_resources import require as pkg_require

from loguru import logger

try:
    __version__: str = pkg_require("busylight-for-humans")[0].version
except Exception as error:
    logger.error(f"Failed to retrieve version string: {error}")
    __version__: str = "unknown"

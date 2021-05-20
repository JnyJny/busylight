"""
"""

import os
from loguru import logger


if os.environ.get("BUSYLIGHT_DEBUG", False):
    logger.enable(__name__)
else:
    logger.disable(__name__)

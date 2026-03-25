"""Logging Configuration for API Integration.

Integrates loguru logging with uvicorn's standard logging to ensure
all API events are properly captured and displayed when running
with uvicorn.
"""

import logging
import sys
from typing import Any, Dict

from loguru import logger


class InterceptHandler(logging.Handler):
    """Intercept standard logging messages and redirect them to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record through loguru."""
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(debug: bool = False) -> None:
    """Setup integrated logging for API server.

    Args:
        debug: Enable debug level logging
    """
    # Remove default loguru handler
    logger.remove()

    # Add loguru handler with appropriate level
    log_level = "DEBUG" if debug else "INFO"

    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        colorize=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [InterceptHandler()]
        uvicorn_logger.propagate = False
        uvicorn_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    if debug:
        logger.debug("Debug logging enabled")

    logger.info("Logging configuration complete")


def get_uvicorn_log_config(debug: bool = False) -> Dict[str, Any]:
    """Get uvicorn logging configuration that integrates with loguru.

    Args:
        debug: Enable debug level logging

    Returns:
        Logging configuration dict for uvicorn
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "busylight.api.logging_config.InterceptHandler",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
        },
    }

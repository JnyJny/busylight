"""FastAPI Middleware for Dynamic Device Management.

Implements middleware to handle USB device hot-plugging/unplugging events.
The light manager middleware runs before each API request to refresh the
available light devices, ensuring the controller stays synchronized with
the current hardware state when devices are connected or disconnected
during runtime.
"""

from typing import Callable

from fastapi import Request, Response
from loguru import logger

from .dependencies import get_light_controller


async def light_manager_middleware(request: Request, call_next: Callable) -> Response:
    """Update light manager for device plug/unplug events before each request."""
    try:
        controller = get_light_controller()
        controller.lights
    except Exception as error:
        logger.debug(f"Light manager update failed: {error}")

    return await call_next(request)

"""FastAPI Application Factory."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from busylight_core import LightUnavailableError, NoLightsFoundError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from ..color import ColorLookupError
from .config import get_settings
from .dependencies import get_light_controller, release_light_controller
from .exceptions import (
    color_lookup_error_handler,
    index_error_handler,
    light_unavailable_handler,
    no_lights_found_handler,
    validation_error_handler,
)
from .logging_config import setup_logging
from .middleware import light_manager_middleware
from .v1.router import legacy_router, v1_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events for startup and shutdown."""
    logger.info("Starting BusyLight API server")
    controller = get_light_controller()
    controller.all().turn_off()
    logger.info(f"Found {len(controller.lights)} light(s)")

    yield

    logger.info("Shutting down BusyLight API server")
    try:
        controller = get_light_controller()
        controller.all().turn_off()
    except Exception as error:
        logger.debug(f"Problem during shutdown: {error}")
    finally:
        release_light_controller()


def create_app() -> FastAPI:
    """Create and configure FastAPI application with middleware and routing."""
    settings = get_settings()

    setup_logging(debug=settings.debug)

    dependencies = []
    if settings.is_auth_enabled:
        logger.info("Authentication enabled via environment variables")
    else:
        logger.info("Authentication disabled, no credentials found in environment")

    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        lifespan=lifespan,
        dependencies=dependencies,
    )

    cors_origins = settings.cors_origins_for_debug
    if cors_origins:
        logger.info(f"CORS enabled for origins: {cors_origins}")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        logger.info("CORS disabled - no origins configured")

    app.middleware("http")(light_manager_middleware)

    app.add_exception_handler(LightUnavailableError, light_unavailable_handler)
    app.add_exception_handler(NoLightsFoundError, no_lights_found_handler)
    app.add_exception_handler(IndexError, index_error_handler)
    app.add_exception_handler(ColorLookupError, color_lookup_error_handler)
    app.add_exception_handler(ValueError, validation_error_handler)

    app.include_router(v1_router)
    app.include_router(legacy_router)

    logger.info("FastAPI application configured successfully")
    return app


app = create_app()

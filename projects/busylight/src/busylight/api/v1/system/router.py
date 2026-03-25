"""System API Routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from ....controller import LightController
from ...config import APISettings, get_settings
from ...dependencies import Controller
from .schemas import ApiInfo, HealthStatus

router = APIRouter(prefix="/system", tags=["system"])


@router.get(
    "/info",
    response_model=ApiInfo,
    summary="API information",
    description="Get API metadata and information.",
)
async def get_api_info(
    settings: Annotated[APISettings, Depends(get_settings)],
) -> ApiInfo:
    """API information."""
    return ApiInfo(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )


@router.get(
    "/health",
    response_model=HealthStatus,
    summary="Health check",
    description="Check API and hardware health status.",
)
async def health_check(
    controller: Controller,
) -> HealthStatus:
    """System health status."""
    lights_count = len(controller.lights)

    if lights_count > 0:
        status = "healthy"
        message = f"API is operational with {lights_count} light(s) available"
    else:
        status = "degraded"
        message = "API is operational but no lights are currently available"

    return HealthStatus(
        status=status,
        lights_available=lights_count,
        message=message,
    )

"""Root API Endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from ..config import APISettings, get_settings

root_router = APIRouter()


@root_router.get(
    "/",
    summary="API root",
    description="Get API information and available endpoints.",
)
async def api_root(
    settings: Annotated[APISettings, Depends(get_settings)],
) -> dict[str, Any]:
    """API information including versions, domains and available endpoints."""
    return {
        "name": "BusyLight API",
        "title": settings.title,
        "version": settings.version,
        "description": settings.description,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
        "api_versions": {
            "v1": {
                "prefix": "/api/v1",
                "description": "Current stable API version",
                "features": [
                    "REST endpoints for light control",
                    "Effects management",
                    "LED targeting for multi-LED devices",
                    "System health monitoring",
                ],
            },
            "legacy": {
                "prefix": "/",
                "description": "Legacy endpoints for backward compatibility",
                "deprecated": True,
                "note": "Includes both POST endpoints and GET endpoints",
            },
        },
        "domains": [
            {
                "name": "lights",
                "description": "Basic light control operations",
                "endpoints": ["/lights", "/lights/{id}"],
            },
            {
                "name": "effects",
                "description": "Advanced light effects",
                "endpoints": ["/effects/rainbow", "/effects/pulse", "/effects/flash"],
            },
            {
                "name": "system",
                "description": "API system information and health",
                "endpoints": ["/system/info", "/system/health"],
            },
        ],
    }

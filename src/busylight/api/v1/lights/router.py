"""Light API Routes."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from ...dependencies import AuthenticatedController, Controller
from .schemas import (
    LightBlinkRequest,
    LightOnRequest,
    LightOperationResponse,
    LightStatus,
)
from .service import LightService

router = APIRouter(prefix="/lights", tags=["lights"])


def get_light_service_public(
    controller: Controller,
) -> LightService:
    """Get light service instance for public endpoints."""
    return LightService(controller)


def get_light_service_auth(
    controller: AuthenticatedController,
) -> LightService:
    """Get light service instance for authenticated endpoints."""
    return LightService(controller)


PublicLightServiceDep = Annotated[LightService, Depends(get_light_service_public)]
AuthLightServiceDep = Annotated[LightService, Depends(get_light_service_auth)]


@router.get(
    "/{light_id}/status",
    response_model=LightStatus,
    summary="Get light status",
    description="Get detailed status information for a specific light.",
)
@router.get(
    "/{light_id}",
    response_model=LightStatus,
    summary="Get light status",
    description="Get detailed status information for a specific light.",
)
async def get_light_status(
    light_id: Annotated[int, Path(description="Light identifier", ge=0)],
    service: PublicLightServiceDep,
) -> LightStatus:
    """Get status of a specific light."""
    return service.get_light_status(light_id)


@router.get(
    "/status",
    response_model=list[LightStatus],
    summary="Get all lights status",
    description="Get status information for all available lights.",
)
@router.get(
    "",
    response_model=list[LightStatus],
    summary="Get all lights status",
    description="Get status information for all available lights.",
)
async def get_all_lights_status(
    service: PublicLightServiceDep,
) -> list[LightStatus]:
    """Get status of all available lights."""
    return service.get_all_lights_status()


@router.post(
    "/{light_id}/on",
    response_model=LightOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Turn on light",
    description="Turn on a specific light with the given color and settings.",
)
async def turn_on_light(
    light_id: Annotated[int, Path(description="Light identifier", ge=0)],
    request: Annotated[LightOnRequest, Body()],
    service: AuthLightServiceDep,
) -> LightOperationResponse:
    """Turn on a specific light."""
    return service.turn_on_light(
        color=request.color,
        dim=request.dim,
        led=request.led,
        light_id=light_id,
    )


@router.post(
    "/on",
    response_model=LightOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Turn on all lights",
    description="Turn on all available lights with the given color and settings.",
)
async def turn_on_all_lights(
    request: Annotated[LightOnRequest, Body()],
    service: AuthLightServiceDep,
) -> LightOperationResponse:
    """Turn on all lights."""
    return service.turn_on_light(
        color=request.color,
        dim=request.dim,
        led=request.led,
        light_id=None,
    )


@router.post(
    "/{light_id}/off",
    response_model=LightOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Turn off light",
    description="Turn off a specific light.",
)
async def turn_off_light(
    light_id: Annotated[int, Path(description="Light identifier", ge=0)],
    service: AuthLightServiceDep,
) -> LightOperationResponse:
    """Turn off a specific light."""
    return service.turn_off_light(light_id=light_id)


@router.post(
    "/off",
    response_model=LightOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Turn off all lights",
    description="Turn off all available lights.",
)
async def turn_off_all_lights(
    service: AuthLightServiceDep,
) -> LightOperationResponse:
    """Turn off all lights."""
    return service.turn_off_light(light_id=None)


@router.post(
    "/{light_id}/blink",
    response_model=LightOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Blink light",
    description="Start blinking a specific light with the given parameters.",
)
async def blink_light(
    light_id: Annotated[int, Path(description="Light identifier", ge=0)],
    request: Annotated[LightBlinkRequest, Body()],
    service: AuthLightServiceDep,
) -> LightOperationResponse:
    """Blink a specific light."""
    return service.blink_light(
        color=request.color,
        dim=request.dim,
        speed=request.speed,
        count=request.count,
        led=request.led,
        light_id=light_id,
    )


@router.post(
    "/blink",
    response_model=LightOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Blink all lights",
    description="Start blinking all available lights with the given parameters.",
)
async def blink_all_lights(
    request: Annotated[LightBlinkRequest, Body()],
    service: AuthLightServiceDep,
) -> LightOperationResponse:
    """Blink all lights."""
    return service.blink_light(
        color=request.color,
        dim=request.dim,
        speed=request.speed,
        count=request.count,
        led=request.led,
        light_id=None,
    )

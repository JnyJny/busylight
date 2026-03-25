"""Effects API Routes."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from ...dependencies import AuthenticatedController
from .schemas import (
    EffectOperationResponse,
    FlashEffectRequest,
    PulseEffectRequest,
    RainbowEffectRequest,
)
from .service import EffectService

router = APIRouter(prefix="/effects", tags=["effects"])


def get_effect_service(
    controller: AuthenticatedController,
) -> EffectService:
    """Get effect service instance."""
    return EffectService(controller)


EffectServiceDep = Annotated[EffectService, Depends(get_effect_service)]


@router.post(
    "/{light_id}/rainbow",
    response_model=EffectOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Rainbow effect on light",
    description="Apply rainbow/spectrum effect to a specific light.",
)
async def rainbow_light_effect(
    light_id: Annotated[int, Path(description="Light identifier", ge=0)],
    request: Annotated[RainbowEffectRequest, Body()],
    service: EffectServiceDep,
) -> EffectOperationResponse:
    """Apply rainbow effect to a specific light."""
    return await service.apply_rainbow_effect(
        dim=request.dim,
        speed=request.speed,
        led=request.led,
        light_id=light_id,
    )


@router.post(
    "/rainbow",
    response_model=EffectOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Rainbow effect on all lights",
    description="Apply rainbow/spectrum effect to all lights.",
)
async def rainbow_all_lights_effect(
    request: Annotated[RainbowEffectRequest, Body()],
    service: EffectServiceDep,
) -> EffectOperationResponse:
    """Apply rainbow effect to all lights."""
    return await service.apply_rainbow_effect(
        dim=request.dim,
        speed=request.speed,
        led=request.led,
        light_id=None,
    )


@router.post(
    "/{light_id}/pulse",
    response_model=EffectOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Pulse effect on light",
    description="Apply pulse/gradient effect to a specific light.",
)
async def pulse_light_effect(
    light_id: Annotated[int, Path(description="Light identifier", ge=0)],
    request: Annotated[PulseEffectRequest, Body()],
    service: EffectServiceDep,
) -> EffectOperationResponse:
    """Apply pulse effect to a specific light."""
    return await service.apply_pulse_effect(
        color=request.color,
        dim=request.dim,
        speed=request.speed,
        count=request.count,
        led=request.led,
        light_id=light_id,
    )


@router.post(
    "/pulse",
    response_model=EffectOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Pulse effect on all lights",
    description="Apply pulse/gradient effect to all lights.",
)
async def pulse_all_lights_effect(
    request: Annotated[PulseEffectRequest, Body()],
    service: EffectServiceDep,
) -> EffectOperationResponse:
    """Apply pulse effect to all lights."""
    return await service.apply_pulse_effect(
        color=request.color,
        dim=request.dim,
        speed=request.speed,
        count=request.count,
        led=request.led,
        light_id=None,
    )


@router.post(
    "/{light_id}/flash",
    response_model=EffectOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Flash effect on light",
    description="Apply flash lights impressively (fli) effect to a specific light.",
)
async def flash_light_effect(
    light_id: Annotated[int, Path(description="Light identifier", ge=0)],
    request: Annotated[FlashEffectRequest, Body()],
    service: EffectServiceDep,
) -> EffectOperationResponse:
    """Apply flash effect to a specific light."""
    return await service.apply_flash_effect(
        color_a=request.color_a,
        color_b=request.color_b,
        dim=request.dim,
        speed=request.speed,
        count=request.count,
        led=request.led,
        light_id=light_id,
    )


@router.post(
    "/flash",
    response_model=EffectOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Flash effect on all lights",
    description="Apply flash lights impressively (fli) effect to all lights.",
)
async def flash_all_lights_effect(
    request: Annotated[FlashEffectRequest, Body()],
    service: EffectServiceDep,
) -> EffectOperationResponse:
    """Apply flash effect to all lights."""
    return await service.apply_flash_effect(
        color_a=request.color_a,
        color_b=request.color_b,
        dim=request.dim,
        speed=request.speed,
        count=request.count,
        led=request.led,
        light_id=None,
    )

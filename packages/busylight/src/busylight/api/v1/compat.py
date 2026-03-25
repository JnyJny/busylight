"""Backward Compatibility Layer.

GET-based endpoints that match the original API structure for backward compatibility.
These endpoints convert query parameters to request body format and delegate to
POST-based endpoints.
"""

from fastapi import APIRouter, Depends, Path, Query

from ..dependencies import AuthenticatedController
from .effects.schemas import EffectOperationResponse
from .effects.service import EffectService
from .lights.schemas import LightOperationResponse
from .lights.service import LightService

compat_router = APIRouter(tags=["compatibility"])


def get_light_service(controller: AuthenticatedController) -> LightService:
    """Light service instance for compatibility endpoints."""
    return LightService(controller)


def get_effect_service(controller: AuthenticatedController) -> EffectService:
    """Effect service instance for compatibility endpoints."""
    return EffectService(controller)


@compat_router.get(
    "/light/{light_id}/on",
    response_model=LightOperationResponse,
    summary="Turn on light (legacy)",
    description="Legacy GET endpoint for turning on a light. Use POST /lights/{light_id}/on instead.",
    deprecated=True,
)
async def legacy_light_on(
    light_id: int = Path(..., description="Light identifier", ge=0),
    color: str = Query("green"),
    dim: float = Query(1.0, ge=0.0, le=1.0),
    led: int = Query(0, ge=0),
    service: LightService = Depends(get_light_service),
) -> LightOperationResponse:
    """Turn on specific light using GET interface."""
    return service.turn_on_light(color=color, dim=dim, led=led, light_id=light_id)


@compat_router.get(
    "/lights/on",
    response_model=LightOperationResponse,
    summary="Turn on all lights (legacy)",
    description="Legacy GET endpoint for turning on all lights. Use POST /lights/on instead.",
    deprecated=True,
)
async def legacy_lights_on(
    color: str = Query("green"),
    dim: float = Query(1.0, ge=0.0, le=1.0),
    led: int = Query(0, ge=0),
    service: LightService = Depends(get_light_service),
) -> LightOperationResponse:
    """Turn on all lights using GET interface."""
    return service.turn_on_light(color=color, dim=dim, led=led, light_id=None)


@compat_router.get(
    "/light/{light_id}/off",
    response_model=LightOperationResponse,
    summary="Turn off light (legacy)",
    description="Legacy GET endpoint for turning off a light. Use POST /lights/{light_id}/off instead.",
    deprecated=True,
)
async def legacy_light_off(
    light_id: int = Path(..., description="Light identifier", ge=0),
    service: LightService = Depends(get_light_service),
) -> LightOperationResponse:
    """Turn off specific light using GET interface."""
    return service.turn_off_light(light_id=light_id)


@compat_router.get(
    "/lights/off",
    response_model=LightOperationResponse,
    summary="Turn off all lights (legacy)",
    description="Legacy GET endpoint for turning off all lights. Use POST /lights/off instead.",
    deprecated=True,
)
async def legacy_lights_off(
    service: LightService = Depends(get_light_service),
) -> LightOperationResponse:
    """Turn off all lights using GET interface."""
    return service.turn_off_light(light_id=None)


@compat_router.get(
    "/light/{light_id}/blink",
    response_model=LightOperationResponse,
    summary="Blink light (legacy)",
    description="Legacy GET endpoint for blinking a light. Use POST /lights/{light_id}/blink instead.",
    deprecated=True,
)
async def legacy_light_blink(
    light_id: int = Path(..., description="Light identifier", ge=0),
    color: str = Query("red"),
    dim: float = Query(1.0, ge=0.0, le=1.0),
    speed: str = Query("slow"),
    count: int = Query(0, ge=0),
    led: int = Query(0, ge=0),
    service: LightService = Depends(get_light_service),
) -> LightOperationResponse:
    """Blink specific light using GET interface."""
    return service.blink_light(
        color=color, dim=dim, speed=speed, count=count, led=led, light_id=light_id
    )


@compat_router.get(
    "/lights/blink",
    response_model=LightOperationResponse,
    summary="Blink all lights (legacy)",
    description="Legacy GET endpoint for blinking all lights. Use POST /lights/blink instead.",
    deprecated=True,
)
async def legacy_lights_blink(
    color: str = Query("red"),
    dim: float = Query(1.0, ge=0.0, le=1.0),
    speed: str = Query("slow"),
    count: int = Query(0, ge=0),
    led: int = Query(0, ge=0),
    service: LightService = Depends(get_light_service),
) -> LightOperationResponse:
    """Blink all lights using GET interface."""
    return service.blink_light(
        color=color, dim=dim, speed=speed, count=count, led=led, light_id=None
    )


@compat_router.get(
    "/light/{light_id}/rainbow",
    response_model=EffectOperationResponse,
    summary="Rainbow effect on light (legacy)",
    description="Legacy GET endpoint for rainbow effect. Use POST /effects/{light_id}/rainbow instead.",
    deprecated=True,
)
async def legacy_light_rainbow(
    light_id: int = Path(..., description="Light identifier", ge=0),
    dim: float = Query(1.0, ge=0.0, le=1.0),
    speed: str = Query("slow"),
    led: int = Query(0, ge=0),
    service: EffectService = Depends(get_effect_service),
) -> EffectOperationResponse:
    """Rainbow effect on specific light using GET interface."""
    return await service.apply_rainbow_effect(
        dim=dim, speed=speed, led=led, light_id=light_id
    )


@compat_router.get(
    "/lights/rainbow",
    response_model=EffectOperationResponse,
    summary="Rainbow effect on all lights (legacy)",
    description="Legacy GET endpoint for rainbow effect. Use POST /effects/rainbow instead.",
    deprecated=True,
)
async def legacy_lights_rainbow(
    dim: float = Query(1.0, ge=0.0, le=1.0),
    speed: str = Query("slow"),
    led: int = Query(0, ge=0),
    service: EffectService = Depends(get_effect_service),
) -> EffectOperationResponse:
    """Rainbow effect on all lights using GET interface."""
    return await service.apply_rainbow_effect(
        dim=dim, speed=speed, led=led, light_id=None
    )


@compat_router.get(
    "/light/{light_id}/pulse",
    response_model=EffectOperationResponse,
    summary="Pulse effect on light (legacy)",
    description="Legacy GET endpoint for pulse effect. Use POST /effects/{light_id}/pulse instead.",
    deprecated=True,
)
async def legacy_light_pulse(
    light_id: int = Path(..., description="Light identifier", ge=0),
    color: str = Query("red"),
    dim: float = Query(1.0, ge=0.0, le=1.0),
    speed: str = Query("slow"),
    count: int = Query(0, ge=0),
    led: int = Query(0, ge=0),
    service: EffectService = Depends(get_effect_service),
) -> EffectOperationResponse:
    """Pulse effect on specific light using GET interface."""
    return await service.apply_pulse_effect(
        color=color, dim=dim, speed=speed, count=count, led=led, light_id=light_id
    )


@compat_router.get(
    "/lights/pulse",
    response_model=EffectOperationResponse,
    summary="Pulse effect on all lights (legacy)",
    description="Legacy GET endpoint for pulse effect. Use POST /effects/pulse instead.",
    deprecated=True,
)
async def legacy_lights_pulse(
    color: str = Query("red"),
    dim: float = Query(1.0, ge=0.0, le=1.0),
    speed: str = Query("slow"),
    count: int = Query(0, ge=0),
    led: int = Query(0, ge=0),
    service: EffectService = Depends(get_effect_service),
) -> EffectOperationResponse:
    """Pulse effect on all lights using GET interface."""
    return await service.apply_pulse_effect(
        color=color, dim=dim, speed=speed, count=count, led=led, light_id=None
    )


@compat_router.get(
    "/light/{light_id}/fli",
    response_model=EffectOperationResponse,
    summary="Flash effect on light (legacy)",
    description="Legacy GET endpoint for flash effect. Use POST /effects/{light_id}/flash instead.",
    deprecated=True,
)
async def legacy_light_fli(
    light_id: int = Path(..., description="Light identifier", ge=0),
    color_a: str = Query("red"),
    color_b: str = Query("blue"),
    dim: float = Query(1.0, ge=0.0, le=1.0),
    speed: str = Query("slow"),
    count: int = Query(0, ge=0),
    led: int = Query(0, ge=0),
    service: EffectService = Depends(get_effect_service),
) -> EffectOperationResponse:
    """Flash effect on specific light using GET interface."""
    return await service.apply_flash_effect(
        color_a=color_a,
        color_b=color_b,
        dim=dim,
        speed=speed,
        count=count,
        led=led,
        light_id=light_id,
    )


@compat_router.get(
    "/lights/fli",
    response_model=EffectOperationResponse,
    summary="Flash effect on all lights (legacy)",
    description="Legacy GET endpoint for flash effect. Use POST /effects/flash instead.",
    deprecated=True,
)
async def legacy_lights_fli(
    color_a: str = Query("red"),
    color_b: str = Query("blue"),
    dim: float = Query(1.0, ge=0.0, le=1.0),
    speed: str = Query("slow"),
    count: int = Query(0, ge=0),
    led: int = Query(0, ge=0),
    service: EffectService = Depends(get_effect_service),
) -> EffectOperationResponse:
    """Flash effect on all lights using GET interface."""
    return await service.apply_flash_effect(
        color_a=color_a,
        color_b=color_b,
        dim=dim,
        speed=speed,
        count=count,
        led=led,
        light_id=None,
    )

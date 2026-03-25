"""API Version 1 Router Assembly."""

from fastapi import APIRouter

from .compat import compat_router
from .effects.router import router as effects_router
from .lights.router import router as lights_router
from .root import root_router
from .system.router import router as system_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(lights_router)
v1_router.include_router(effects_router)
v1_router.include_router(system_router)

legacy_router = APIRouter()

legacy_router.include_router(root_router)
legacy_router.include_router(lights_router)
legacy_router.include_router(effects_router)
legacy_router.include_router(system_router)
legacy_router.include_router(compat_router)

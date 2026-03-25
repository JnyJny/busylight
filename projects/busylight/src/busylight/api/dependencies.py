"""FastAPI Dependency Injection System.

Provides dependency injection for:
- Light controller singleton management with lifecycle handling
- HTTP Basic Authentication with configurable credentials
- Type aliases for controller access patterns (public vs authenticated)

The dependency system enables clean separation between public endpoints
(system info, health checks) and protected endpoints (light control operations)
while maintaining a single controller instance across the application lifecycle.
"""

from secrets import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from ..controller import LightController
from .config import APISettings, get_settings

_light_controller: LightController | None = None
_http_basic = HTTPBasic()


def get_light_controller() -> LightController:
    """Global light controller singleton instance."""
    global _light_controller
    if _light_controller is None:
        _light_controller = LightController()
    return _light_controller


def release_light_controller() -> None:
    """Release and cleanup the global light controller."""
    global _light_controller
    if _light_controller is not None:
        _light_controller.release_lights()
        _light_controller = None


def authenticate_user(
    request: Request,
    settings: Annotated[APISettings, Depends(get_settings)],
) -> None:
    """Authenticate user with HTTP Basic Auth when enabled."""
    if not settings.is_auth_enabled:
        return

    credentials = _http_basic(request)

    username_correct = compare_digest(credentials.username, settings.username or "")
    password_correct = compare_digest(credentials.password, settings.password or "")

    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def get_authenticated_controller(
    controller: Annotated[LightController, Depends(get_light_controller)],
    _: Annotated[None, Depends(authenticate_user)],
) -> LightController:
    """Light controller instance with authentication verification."""
    return controller


Controller = Annotated[LightController, Depends(get_light_controller)]
AuthenticatedController = Annotated[
    LightController, Depends(get_authenticated_controller)
]
Settings = Annotated[APISettings, Depends(get_settings)]

"""BusyLight API.

Modern FastAPI-based REST API for controlling USB LED lights.

This module provides a restructured API following FastAPI best practices:
- Domain-based organization (lights, effects, system)
- Proper separation of concerns (routers, services, schemas)
- API versioning support (v1, v2)
- Modern patterns (dependency injection, Pydantic models, proper HTTP methods)
"""

from .main import app as busylightapi
from .models import EndPoint, LightDescription, LightOperation

__all__ = [
    "EndPoint",
    "LightDescription",
    "LightOperation",
    "busylightapi",
]

"""API Response Models"""

from typing import Any

from pydantic import BaseModel


class LightOperation(BaseModel):
    """Result of a light or effect operation."""

    light_id: int | str
    action: str | None = None
    color: str | None = None
    rgb: tuple[int, int, int] | None = None
    speed: str | None = None
    name: str | None = None
    dim: float = 1.0


class LightDescription(BaseModel):
    """Description of a single light's identity and current state."""

    light_id: int
    name: str
    info: dict[str, Any]
    is_on: bool
    color: str
    rgb: tuple[int, int, int]


class EndPoint(BaseModel):
    """A single API route path."""

    path: str

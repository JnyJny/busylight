"""API Response Models"""

from typing import Any

from pydantic import BaseModel


class LightOperation(BaseModel):
    light_id: int | str
    action: str | None = None
    color: str | None = None
    rgb: tuple[int, int, int] | None = None
    speed: str | None = None
    name: str | None = None
    dim: float = 1.0


class LightDescription(BaseModel):
    light_id: int
    name: str
    info: dict[str, Any]
    is_on: bool
    color: str
    rgb: tuple[int, int, int]


class EndPoint(BaseModel):
    path: str

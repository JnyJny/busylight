"""API Response Models
"""

from typing import Dict, Tuple, Union, Optional

from pydantic import BaseModel


class LightOperation(BaseModel):
    light_id: Union[int, str]
    action: Optional[str] = None
    color: Optional[str] = None
    rgb: Optional[Tuple[int, int, int]] = None
    speed: Optional[str] = None
    name: Optional[str] = None
    dim: Optional[float] = 1.0


class LightDescription(BaseModel):
    light_id: int
    name: str
    info: Dict[str, Union[int, str, Tuple[int, int]]]
    is_on: bool
    color: str
    rgb: Tuple[int, int, int]


class EndPoint(BaseModel):
    path: str

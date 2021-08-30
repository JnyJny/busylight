"""API Response Models
"""

from typing import Dict, Union, Optional

from pydantic import BaseModel


class LightOperation(BaseModel):
    light_id: Union[int, str]
    action: Optional[str] = None
    color: Optional[str] = None
    speed: Optional[str] = None
    name: Optional[str] = None


class LightDescription(BaseModel):
    light_id: int
    name: str
    info: Dict[str, Union[int, str]]
    is_on: bool
    color: str


class EndPoint(BaseModel):
    path: str

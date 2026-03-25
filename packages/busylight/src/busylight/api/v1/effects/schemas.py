"""Effects API Schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class RainbowEffectRequest(BaseModel):
    """Request for rainbow/spectrum effect."""

    dim: float = Field(
        default=1.0, description="Brightness level (0.0-1.0)", ge=0.0, le=1.0
    )
    speed: Literal["slow", "medium", "fast"] = Field(
        default="slow", description="Effect speed"
    )
    led: int = Field(default=0, description="LED index (0=all, 1+=specific)", ge=0)


class PulseEffectRequest(BaseModel):
    """Request for pulse/gradient effect."""

    color: str = Field(default="red", description="Color name or hex string")
    dim: float = Field(
        default=1.0, description="Brightness level (0.0-1.0)", ge=0.0, le=1.0
    )
    speed: Literal["slow", "medium", "fast"] = Field(
        default="slow", description="Effect speed"
    )
    count: int = Field(default=0, description="Number of pulses (0=infinite)", ge=0)
    led: int = Field(default=0, description="LED index (0=all, 1+=specific)", ge=0)


class FlashEffectRequest(BaseModel):
    """Request for flash lights impressively (fli) effect."""

    color_a: str = Field(default="red", description="First color name or hex string")
    color_b: str = Field(default="blue", description="Second color name or hex string")
    dim: float = Field(
        default=1.0, description="Brightness level (0.0-1.0)", ge=0.0, le=1.0
    )
    speed: Literal["slow", "medium", "fast"] = Field(
        default="slow", description="Effect speed"
    )
    count: int = Field(default=0, description="Number of flashes (0=infinite)", ge=0)
    led: int = Field(default=0, description="LED index (0=all, 1+=specific)", ge=0)


class EffectOperationResponse(BaseModel):
    """Response from an effect operation."""

    success: bool = Field(description="Whether operation was successful")
    action: str = Field(description="Action performed")
    effect_name: str = Field(description="Name of effect applied")
    light_id: int | str = Field(description="Light ID or 'all'")
    color: str | None = Field(default=None, description="Color used")
    rgb: tuple[int, int, int] | None = Field(
        default=None, description="RGB values used"
    )
    dim: float | None = Field(default=None, description="Brightness level used")
    speed: str | None = Field(default=None, description="Speed used")
    count: int | None = Field(default=None, description="Count used")
    led: int | None = Field(default=None, description="LED index used")
    message: str | None = Field(default=None, description="Additional message")

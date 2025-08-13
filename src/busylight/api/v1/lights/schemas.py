"""Light API Schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class LightHardwareInfo(BaseModel):
    """Hardware information for a light device."""

    path: str = Field(description="Device path")
    vendor_id: int = Field(description="USB vendor ID")
    product_id: int = Field(description="USB product ID")
    serial_number: str | None = Field(description="Device serial number")
    manufacturer_string: str | None = Field(description="Manufacturer string")
    product_string: str | None = Field(description="Product string")
    release_number: int | None = Field(description="Device release number")
    is_acquired: bool = Field(description="Whether device is currently acquired")


class LightStatus(BaseModel):
    """Current status of a light."""

    light_id: int = Field(description="Numeric light identifier", ge=0)
    name: str = Field(description="Light device name")
    info: LightHardwareInfo = Field(description="Hardware information")
    is_on: bool = Field(description="Whether light is currently on")
    color: str = Field(description="Current color name")
    rgb: tuple[int, int, int] = Field(description="Current RGB values")


class LightOnRequest(BaseModel):
    """Request to turn on a light."""

    color: str = Field(default="green", description="Color name or hex string")
    dim: float = Field(
        default=1.0, description="Brightness level (0.0-1.0)", ge=0.0, le=1.0
    )
    led: int = Field(default=0, description="LED index (0=all, 1+=specific)", ge=0)


class LightBlinkRequest(BaseModel):
    """Request to blink a light."""

    color: str = Field(default="red", description="Color name or hex string")
    dim: float = Field(
        default=1.0, description="Brightness level (0.0-1.0)", ge=0.0, le=1.0
    )
    speed: Literal["slow", "medium", "fast"] = Field(
        default="slow", description="Blink speed"
    )
    count: int = Field(default=0, description="Number of blinks (0=infinite)", ge=0)
    led: int = Field(default=0, description="LED index (0=all, 1+=specific)", ge=0)


class LightOperationResponse(BaseModel):
    """Response from a light operation."""

    success: bool = Field(description="Whether operation was successful")
    action: str = Field(description="Action performed")
    light_id: int | str = Field(description="Light ID or 'all'")
    color: str | None = Field(default=None, description="Color used")
    rgb: tuple[int, int, int] | None = Field(
        default=None, description="RGB values used"
    )
    dim: float | None = Field(default=None, description="Brightness level used")
    led: int | None = Field(default=None, description="LED index used")
    speed: str | None = Field(default=None, description="Speed used")
    count: int | None = Field(default=None, description="Count used")
    message: str | None = Field(default=None, description="Additional message")

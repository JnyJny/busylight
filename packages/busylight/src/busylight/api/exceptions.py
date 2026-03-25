"""Custom Exception Handlers."""

from typing import Any

from busylight_core import LightUnavailableError, NoLightsFoundError
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from ..color import ColorLookupError


class APIError(HTTPException):
    """Base API exception with standardized format."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class LightNotFoundError(APIError):
    """Light not found at specified index."""

    def __init__(self, light_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Light with ID {light_id} not found",
            error_code="LIGHT_NOT_FOUND",
        )


class NoLightsAvailableError(APIError):
    """No lights are currently available."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No USB lights are currently available",
            error_code="NO_LIGHTS_AVAILABLE",
        )


class InvalidColorError(APIError):
    """Invalid color specification."""

    def __init__(self, color: str, reason: str | None = None) -> None:
        detail = f"Invalid color '{color}'"
        if reason:
            detail += f": {reason}"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_COLOR",
        )


class LightUnavailableAPIError(APIError):
    """Light is unavailable for operation."""

    def __init__(self, light_name: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Light '{light_name}' is currently unavailable",
            error_code="LIGHT_UNAVAILABLE",
        )


def create_error_response(
    status_code: int,
    message: str,
    error_code: str | None = None,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Standardized error response with consistent format."""
    content = {
        "error": True,
        "message": message,
        "status_code": status_code,
    }

    if error_code:
        content["error_code"] = error_code
    if details:
        content["details"] = details

    return JSONResponse(status_code=status_code, content=content)


async def light_unavailable_handler(
    request: Request, exc: LightUnavailableError
) -> JSONResponse:
    """Handle lights which are unavailable."""
    return create_error_response(
        status_code=status.HTTP_409_CONFLICT,
        message=str(exc),
        error_code="LIGHT_UNAVAILABLE",
    )


async def no_lights_found_handler(
    request: Request, exc: NoLightsFoundError
) -> JSONResponse:
    """Handle when no lights are found."""
    return create_error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        message="No USB lights are currently available",
        error_code="NO_LIGHTS_AVAILABLE",
    )


async def index_error_handler(request: Request, exc: IndexError) -> JSONResponse:
    """Handle light not found at index."""
    return create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message=str(exc),
        error_code="LIGHT_NOT_FOUND",
    )


async def color_lookup_error_handler(
    request: Request, exc: ColorLookupError
) -> JSONResponse:
    """Handle invalid color specifications."""
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=str(exc),
        error_code="INVALID_COLOR",
    )


async def validation_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle general validation errors."""
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=str(exc),
        error_code="VALIDATION_ERROR",
    )

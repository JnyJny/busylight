"""API Configuration Management."""

import json
from functools import lru_cache
from importlib.metadata import version
from os import environ
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, ValidationError, field_validator


class APISettings(BaseModel):
    """API configuration settings with validation."""

    debug: bool = Field(default=False, description="Enable debug mode")
    title: str = Field(
        default="Busylight Server: A USB Light Server", description="API title"
    )
    description: str = Field(
        default="An API server for USB connected presence lights.",
        description="API description",
    )
    version: str = Field(
        default_factory=lambda: version("busylight-for-humans"),
        description="Package version",
    )
    username: str | None = Field(
        default=None, description="API username for basic auth"
    )
    password: str | None = Field(
        default=None, description="API password for basic auth"
    )
    cors_origins: list[str] = Field(
        default_factory=list, description="Allowed CORS origins"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from environment variable."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list) and all(
                    isinstance(item, str) for item in parsed
                ):
                    return parsed
                else:
                    logger.warning(f"Invalid CORS origins format: {parsed}")
                    return []
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse CORS origins: {v}")
                return []
        elif isinstance(v, list):
            return v
        return []

    @property
    def is_auth_enabled(self) -> bool:
        """Whether authentication is enabled based on credentials presence."""
        return self.username is not None and self.password is not None

    @property
    def cors_origins_for_debug(self) -> list[str]:
        """CORS origins with debug mode fallback to localhost."""
        if self.debug and not self.cors_origins:
            return ["http://localhost", "http://127.0.0.1"]
        return self.cors_origins


def get_api_settings_from_env() -> APISettings:
    """Create API settings from environment variables."""
    try:
        debug = environ.get("BUSYLIGHT_DEBUG", "false").lower() in ("true", "1", "yes")
        username = environ.get("BUSYLIGHT_API_USER") or environ.get(
            "BUSYLIGHT_USERNAME"
        )
        password = environ.get("BUSYLIGHT_API_PASS") or environ.get(
            "BUSYLIGHT_PASSWORD"
        )
        cors_origins_str = (
            environ.get("BUSYLIGHT_API_CORS_ORIGINS_LIST")
            or environ.get("BUSYLIGHT_CORS_ORIGINS")
            or "[]"
        )

        cors_origins: list[str] = []
        if cors_origins_str and cors_origins_str != "[]":
            try:
                parsed = json.loads(cors_origins_str)
                if isinstance(parsed, list) and all(
                    isinstance(item, str) for item in parsed
                ):
                    cors_origins = parsed
                else:
                    logger.warning(f"Invalid CORS origins format: {parsed}")
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse CORS origins: {cors_origins_str}")

        return APISettings(
            debug=debug,
            username=username,
            password=password,
            cors_origins=cors_origins,
        )
    except ValidationError as error:
        logger.error(f"Configuration validation error: {error}")
        raise


@lru_cache()
def get_settings() -> APISettings:
    """Cached API settings instance."""
    return get_api_settings_from_env()

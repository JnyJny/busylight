"""System API Schemas."""

from pydantic import BaseModel, Field


class ApiEndpoint(BaseModel):
    """API endpoint information."""

    path: str = Field(description="Endpoint path")
    methods: list[str] = Field(description="HTTP methods supported")
    summary: str | None = Field(default=None, description="Endpoint summary")
    tags: list[str] = Field(default_factory=list, description="Endpoint tags")


class ApiInfo(BaseModel):
    """API information and metadata."""

    title: str = Field(description="API title")
    description: str = Field(description="API description")
    version: str = Field(description="API version")
    docs_url: str | None = Field(description="Documentation URL")
    redoc_url: str | None = Field(description="ReDoc URL")
    openapi_url: str | None = Field(description="OpenAPI schema URL")


class HealthStatus(BaseModel):
    """Health check response."""

    status: str = Field(description="Health status")
    lights_available: int = Field(description="Number of available lights")
    message: str | None = Field(default=None, description="Additional message")

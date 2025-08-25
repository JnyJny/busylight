"""Tests for the new API structure."""

import pytest
from fastapi.testclient import TestClient
from src.busylight.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAPIStructure:
    """Test the new API structure."""

    def test_app_creation(self):
        """Test that the FastAPI app is created successfully."""
        assert app is not None
        assert app.title == "Busylight Server: A USB Light Server"

    def test_route_counts(self, client):
        """Test that we have the expected number of routes."""
        routes_with_paths = [route for route in app.routes if hasattr(route, "path")]
        # Should have both versioned and legacy routes
        assert len(routes_with_paths) > 40  # Conservative estimate

    def test_root_endpoint(self, client):
        """Test the root API information endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "api_versions" in data
        assert "domains" in data

        # Check API versions
        assert "v1" in data["api_versions"]
        assert "legacy" in data["api_versions"]

    def test_system_health_endpoint(self, client):
        """Test the system health endpoint."""
        response = client.get("/system/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "lights_available" in data
        assert data["status"] in ["healthy", "degraded"]

    def test_system_info_endpoint(self, client):
        """Test the system info endpoint."""
        response = client.get("/system/info")
        assert response.status_code == 200

        data = response.json()
        assert "title" in data
        assert "version" in data
        assert "description" in data

    def test_versioned_routes_exist(self, client):
        """Test that versioned API routes exist."""
        # Test v1 versioned routes that don't require auth
        public_v1_routes = [
            "/api/v1/system/health",
        ]

        for route in public_v1_routes:
            response = client.get(route)
            assert response.status_code == 200

        # Test that auth-required routes return 401 without credentials
        auth_required_routes = [
            "/api/v1/lights",
        ]

        for route in auth_required_routes:
            response = client.get(route)
            # Should return 401 without auth, or 200 if no auth is configured
            assert response.status_code in [200, 401]

    def test_legacy_compatibility_routes(self, client):
        """Test that legacy GET-based routes work."""
        # Test legacy GET routes that require auth
        legacy_routes = [
            "/lights/on?color=red",
            "/lights/off",
            "/lights/rainbow?dim=0.5",
        ]

        for route in legacy_routes:
            response = client.get(route)
            # Should return 401 without auth, 422 for validation errors, 503 if no lights, or 200 if successful
            assert response.status_code in [200, 401, 422, 503]

    def test_openapi_docs_available(self, client):
        """Test that OpenAPI documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/openapi.json")
        assert response.status_code == 200

        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "paths" in openapi_spec
        assert "info" in openapi_spec


class TestDomainSeparation:
    """Test that domains are properly separated."""

    def test_lights_domain_routes(self, client):
        """Test lights domain routes."""
        # Modern POST endpoints
        lights_post_data = {"color": "red", "dim": 1.0, "led": 0}

        # Test lights status (should work)
        response = client.get("/lights")
        assert response.status_code in [200, 401]  # 401 if auth required

        # Test POST endpoints (may fail due to no lights, but shouldn't be 404)
        response = client.post("/lights/on", json=lights_post_data)
        assert response.status_code in [
            200,
            401,
            503,
        ]  # 503 if no lights available, 401 if auth required

    def test_effects_domain_routes(self, client):
        """Test effects domain routes."""
        effect_data = {"dim": 0.5, "speed": "fast", "led": 0}

        response = client.post("/effects/rainbow", json=effect_data)
        assert response.status_code in [
            200,
            401,
            503,
        ]  # 503 if no lights available, 401 if auth required

    def test_system_domain_routes(self, client):
        """Test system domain routes."""
        # System endpoints should always work
        response = client.get("/system/health")
        assert response.status_code == 200

        response = client.get("/system/info")
        assert response.status_code == 200


class TestBackwardCompatibility:
    """Test backward compatibility features."""

    def test_legacy_get_endpoints_marked_deprecated(self, client):
        """Test that legacy GET endpoints are marked as deprecated in OpenAPI."""
        response = client.get("/openapi.json")
        openapi_spec = response.json()

        # Check that legacy GET endpoints are deprecated
        legacy_paths = [
            "/light/{light_id}/on",
            "/lights/blink",
            "/lights/rainbow",
        ]

        for path in legacy_paths:
            if path in openapi_spec["paths"]:
                get_spec = openapi_spec["paths"][path].get("get", {})
                if get_spec:
                    assert get_spec.get("deprecated") is True

    def test_both_versioned_and_legacy_routes_work(self, client):
        """Test that both versioned and legacy routes work."""
        # Legacy route
        response = client.get("/lights")
        assert response.status_code in [200, 401]

        # Versioned route
        response = client.get("/api/v1/lights")
        assert response.status_code in [200, 401]

        # If both work, they should return similar data structure
        if response.status_code == 200:
            legacy_response = client.get("/lights")
            if legacy_response.status_code == 200:
                legacy_data = legacy_response.json()
                versioned_data = response.json()

                # Should have same structure (both are list of light statuses)
                assert type(legacy_data) == type(versioned_data)
                assert isinstance(legacy_data, list)


class TestErrorHandling:
    """Test error handling and responses."""

    def test_404_for_nonexistent_routes(self, client):
        """Test 404 responses for non-existent routes."""
        response = client.get("/nonexistent/route")
        assert response.status_code == 404

    def test_invalid_light_id_handling(self, client):
        """Test handling of invalid light IDs."""
        # Test with very large light ID (should return 404 or proper error)
        response = client.get("/lights/999/status")
        assert response.status_code in [200, 401, 404, 503]  # 401 if auth required

        if response.status_code == 404:
            error_data = response.json()
            # FastAPI uses 'detail' field for error messages
            assert (
                "error" in error_data
                or "message" in error_data
                or "detail" in error_data
            )

    def test_validation_errors(self, client):
        """Test parameter validation."""
        # Invalid data should return 422 or 401 if auth required
        invalid_data = {"color": "red", "dim": 5.0}  # dim > 1.0
        response = client.post("/lights/on", json=invalid_data)
        assert response.status_code in [
            401,
            422,
        ]  # 401 if auth required, 422 for validation

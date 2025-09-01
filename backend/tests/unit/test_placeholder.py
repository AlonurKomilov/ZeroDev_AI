"""
Real unit tests for core functionality
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.settings import settings


client = TestClient(app)


def test_health_check():
    """Test that the API health check endpoint works"""
    response = client.get("/")
    assert response.status_code == 200


def test_settings_configuration():
    """Test that settings are properly configured"""
    assert settings.ENVIRONMENT in ["development", "production"]
    assert settings.JWT_SECRET is not None
    assert len(settings.JWT_SECRET) > 10  # Minimum security


def test_cors_configuration():
    """Test CORS headers are properly set"""
    response = client.options("/", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    # Should allow CORS for development
    assert response.status_code in [200, 204]


@pytest.mark.parametrize("endpoint", [
    "/auth/register",
    "/auth/login", 
    "/api/projects",
    "/api/keys"
])
def test_api_endpoints_exist(endpoint):
    """Test that critical API endpoints exist (even if they require auth)"""
    response = client.get(endpoint)
    # Should not return 404 (endpoint exists)
    assert response.status_code != 404


def test_emergency_api_security():
    """Test that emergency API requires proper authentication"""
    response = client.post("/api/emergency/override", json={"action": "SAFE_MODE"})
    # Should require authentication
    assert response.status_code in [401, 403]


def test_admin_dashboard_security():
    """Test that admin dashboard requires proper authentication"""
    response = client.get("/api/dashboard/health")
    # Should require special authentication
    assert response.status_code in [401, 403]

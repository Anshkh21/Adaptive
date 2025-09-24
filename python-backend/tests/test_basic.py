"""
Basic tests for Python backend
"""

import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Python Backend" in data["message"]

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["backend"] == "python"

@pytest.mark.asyncio
async def test_docs_endpoint():
    """Test API documentation endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/docs")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_redoc_endpoint():
    """Test ReDoc documentation endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/redoc")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_auth_endpoints():
    """Test authentication endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test register endpoint (should return validation error without data)
        response = await ac.post("/api/auth/register")
        assert response.status_code == 422  # Validation error
        
        # Test login endpoint (should return validation error without data)
        response = await ac.post("/api/auth/login")
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_assessments_endpoint():
    """Test assessments endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test without authentication (should return 401)
        response = await ac.get("/api/assessments/")
        assert response.status_code == 401  # Unauthorized

@pytest.mark.asyncio
async def test_404_handler():
    """Test 404 handler"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "Route not found" in data["message"]

if __name__ == "__main__":
    pytest.main([__file__])

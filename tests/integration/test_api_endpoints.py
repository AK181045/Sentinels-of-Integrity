"""
=============================================================================
SENTINELS OF INTEGRITY — Integration Test: API Endpoints
Tests the full request/response cycle through FastAPI.
=============================================================================
"""

import pytest
from httpx import AsyncClient, ASGITransport
from api.app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

    @pytest.mark.asyncio
    async def test_readiness_probe(self, client):
        response = await client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True


class TestDetectionEndpoint:
    """Integration tests for POST /api/v1/detect."""

    @pytest.mark.asyncio
    async def test_detect_valid_request(self, client):
        payload = {
            "media_hash": "a" * 64,
            "media_url": "https://www.youtube.com/watch?v=test123",
            "platform": "youtube",
            "media_type": "video",
        }
        response = await client.post("/api/v1/detect", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data
        assert "sentinels_score" in data
        assert "verdict" in data
        assert data["verdict"] in ["authentic", "suspicious", "synthetic"]
        assert 0 <= data["sentinels_score"] <= 100

    @pytest.mark.asyncio
    async def test_detect_invalid_hash(self, client):
        payload = {
            "media_hash": "tooshort",
            "media_url": "https://youtube.com/watch?v=abc",
            "platform": "youtube",
        }
        response = await client.post("/api/v1/detect", json=payload)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_detect_invalid_platform(self, client):
        payload = {
            "media_hash": "a" * 64,
            "media_url": "https://instagram.com/p/abc",
            "platform": "instagram",
        }
        response = await client.post("/api/v1/detect", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_detect_missing_fields(self, client):
        response = await client.post("/api/v1/detect", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_detect_response_structure(self, client):
        payload = {
            "media_hash": "b" * 64,
            "media_url": "https://x.com/user/status/123456",
            "platform": "twitter",
        }
        response = await client.post("/api/v1/detect", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "ml_result" in data
        assert "blockchain_result" in data
        assert "is_synthetic" in data["ml_result"]
        assert "confidence" in data["ml_result"]
        assert "is_registered" in data["blockchain_result"]


class TestVerificationEndpoint:
    """Integration tests for GET /api/v1/verify."""

    @pytest.mark.asyncio
    async def test_verify_valid_hash(self, client):
        response = await client.get("/api/v1/verify", params={"media_hash": "c" * 64})
        assert response.status_code == 200
        data = response.json()
        assert "is_registered" in data
        assert "content_hash" in data

    @pytest.mark.asyncio
    async def test_verify_invalid_hash(self, client):
        response = await client.get("/api/v1/verify", params={"media_hash": "short"})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_with_history(self, client):
        response = await client.get(
            "/api/v1/verify",
            params={"media_hash": "d" * 64, "include_history": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert "edit_history" in data


class TestReportsEndpoint:
    """Integration tests for /api/v1/reports."""

    @pytest.mark.asyncio
    async def test_list_reports(self, client):
        response = await client.get("/api/v1/reports")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_list_reports_with_filters(self, client):
        response = await client.get(
            "/api/v1/reports",
            params={"platform": "youtube", "limit": 5},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_report_not_found(self, client):
        response = await client.get("/api/v1/reports/nonexistent-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_stats_summary(self, client):
        response = await client.get("/api/v1/reports/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_analyses" in data

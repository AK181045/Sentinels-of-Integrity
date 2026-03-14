"""
=============================================================================
SENTINELS OF INTEGRITY — Integration Test: Rate Limiter
Tests Redis-based sliding window rate limiting middleware.
=============================================================================
"""

import pytest
from httpx import AsyncClient, ASGITransport
from api.app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestRateLimiter:
    """Integration tests for rate limiting middleware."""

    @pytest.mark.asyncio
    async def test_rate_limit_headers_present(self, client):
        """Response should include rate limit headers."""
        response = await client.get("/api/v1/reports")
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    @pytest.mark.asyncio
    async def test_health_bypasses_rate_limit(self, client):
        """Health endpoints should not be rate limited."""
        for _ in range(150):
            response = await client.get("/api/v1/health")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limit_decrements(self, client):
        """Remaining count should decrease with each request."""
        r1 = await client.get("/api/v1/reports")
        r2 = await client.get("/api/v1/reports")
        remaining1 = int(r1.headers.get("X-RateLimit-Remaining", 0))
        remaining2 = int(r2.headers.get("X-RateLimit-Remaining", 0))
        assert remaining2 < remaining1


class TestInputSanitizationMiddleware:
    """Integration tests for input sanitization."""

    @pytest.mark.asyncio
    async def test_xss_in_query_param_rejected(self, client):
        """Query parameters with script tags should be rejected."""
        response = await client.get(
            "/api/v1/verify",
            params={"media_hash": '<script>alert("xss")</script>'},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_sql_injection_in_query_rejected(self, client):
        """SQL injection in query params should be rejected."""
        response = await client.get(
            "/api/v1/verify",
            params={"media_hash": "'; DROP TABLE reports;--"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_path_traversal_rejected(self, client):
        """Path traversal attempts should be rejected."""
        response = await client.get(
            "/api/v1/verify",
            params={"media_hash": "../../../etc/passwd"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_valid_content_type_accepted(self, client):
        """Valid JSON content type should be accepted."""
        payload = {
            "media_hash": "a" * 64,
            "media_url": "https://youtube.com/watch?v=abc",
            "platform": "youtube",
        }
        response = await client.post(
            "/api/v1/detect",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [200, 422]  # 422 if other validation fails

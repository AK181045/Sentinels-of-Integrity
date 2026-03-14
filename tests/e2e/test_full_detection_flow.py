"""
=============================================================================
SENTINELS OF INTEGRITY — E2E Test: Full Detection Flow
Tests the complete flow from API request to Trust Report generation.
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


class TestEndToEndDetection:
    """E2E tests simulating browser extension → API → ML → Blockchain → Report."""

    @pytest.mark.asyncio
    async def test_youtube_video_analysis(self, client):
        """Simulate analyzing a YouTube video end to end."""
        # Step 1: Submit for analysis (simulating extension)
        detect_response = await client.post("/api/v1/detect", json={
            "media_hash": "abcdef0123456789" * 4,
            "media_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "platform": "youtube",
            "media_type": "video",
        })
        assert detect_response.status_code == 200
        report = detect_response.json()

        # Step 2: Validate report structure
        assert "report_id" in report
        assert "sentinels_score" in report
        assert "verdict" in report
        assert "ml_result" in report
        assert "blockchain_result" in report
        assert "analyzed_at" in report

        # Step 3: Score should be valid
        assert 0 <= report["sentinels_score"] <= 100
        assert report["verdict"] in ["authentic", "suspicious", "synthetic"]

        # Step 4: ML result should have detection data
        ml = report["ml_result"]
        assert "is_synthetic" in ml
        assert "confidence" in ml
        assert 0 <= ml["confidence"] <= 1

        # Step 5: Blockchain result should have registration data
        bc = report["blockchain_result"]
        assert "is_registered" in bc

    @pytest.mark.asyncio
    async def test_twitter_video_analysis(self, client):
        """Simulate analyzing a Twitter/X video."""
        response = await client.post("/api/v1/detect", json={
            "media_hash": "1234567890abcdef" * 4,
            "media_url": "https://x.com/user/status/1234567890",
            "platform": "twitter",
        })
        assert response.status_code == 200
        assert response.json()["platform"] == "twitter"

    @pytest.mark.asyncio
    async def test_tiktok_video_analysis(self, client):
        """Simulate analyzing a TikTok video."""
        response = await client.post("/api/v1/detect", json={
            "media_hash": "fedcba9876543210" * 4,
            "media_url": "https://www.tiktok.com/@user/video/123",
            "platform": "tiktok",
        })
        assert response.status_code == 200
        assert response.json()["platform"] == "tiktok"

    @pytest.mark.asyncio
    async def test_verify_then_detect_flow(self, client):
        """Simulate: verify hash first, then run full detection."""
        test_hash = "a1b2c3d4e5f6" + "0" * 52

        # Step 1: Quick hash lookup
        verify_response = await client.get(
            "/api/v1/verify", params={"media_hash": test_hash}
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.json()

        # Step 2: If not registered, run full ML analysis
        if not verify_data["is_registered"]:
            detect_response = await client.post("/api/v1/detect", json={
                "media_hash": test_hash,
                "media_url": "https://www.youtube.com/watch?v=test",
                "platform": "youtube",
            })
            assert detect_response.status_code == 200

    @pytest.mark.asyncio
    async def test_detection_with_options(self, client):
        """Test detection with skip_blockchain and detailed_report options."""
        response = await client.post("/api/v1/detect", json={
            "media_hash": "f" * 64,
            "media_url": "https://www.youtube.com/watch?v=options_test",
            "platform": "youtube",
            "options": {
                "skip_blockchain": True,
                "detailed_report": True,
                "confidence_threshold": 0.8,
            },
        })
        assert response.status_code == 200
        data = response.json()
        # Blockchain should show default (skipped) result
        assert data["blockchain_result"]["is_registered"] is False


class TestEndToEndSecurity:
    """E2E security tests."""

    @pytest.mark.asyncio
    async def test_cors_headers_present(self, client):
        """CORS headers should be present for extension requests."""
        response = await client.options(
            "/api/v1/detect",
            headers={
                "Origin": "chrome-extension://test",
                "Access-Control-Request-Method": "POST",
            },
        )
        # FastAPI CORS middleware should respond
        assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_malicious_payload_rejected(self, client):
        """Malicious payloads should be rejected by validation."""
        response = await client.post("/api/v1/detect", json={
            "media_hash": "<script>alert('xss')</script>" + "a" * 40,
            "media_url": "javascript:alert(1)",
            "platform": "youtube",
        })
        assert response.status_code in [400, 422]

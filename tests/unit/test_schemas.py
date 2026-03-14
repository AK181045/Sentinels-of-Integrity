"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Pydantic Schemas
Tests request/response model validation.
=============================================================================
"""

import pytest
from pydantic import ValidationError
from api.app.models.schemas import (
    MediaAnalysisRequest,
    AnalysisOptions,
    Platform,
    MediaType,
    MLResultResponse,
    BlockchainVerificationResponse,
    TrustReportSummary,
    Verdict,
    AnalysisStatus,
)


class TestMediaAnalysisRequest:
    """Tests for MediaAnalysisRequest validation."""

    def test_valid_request(self):
        req = MediaAnalysisRequest(
            media_hash="a" * 64,
            media_url="https://www.youtube.com/watch?v=abc",
            platform=Platform.YOUTUBE,
        )
        assert req.media_hash == "a" * 64

    def test_hash_too_short_rejected(self):
        with pytest.raises(ValidationError):
            MediaAnalysisRequest(
                media_hash="abc",
                media_url="https://youtube.com/watch?v=abc",
                platform=Platform.YOUTUBE,
            )

    def test_hash_too_long_rejected(self):
        with pytest.raises(ValidationError):
            MediaAnalysisRequest(
                media_hash="a" * 65,
                media_url="https://youtube.com/watch?v=abc",
                platform=Platform.YOUTUBE,
            )

    def test_hash_non_hex_rejected(self):
        with pytest.raises(ValidationError):
            MediaAnalysisRequest(
                media_hash="g" * 64,  # 'g' is not valid hex
                media_url="https://youtube.com/watch?v=abc",
                platform=Platform.YOUTUBE,
            )

    def test_hash_normalized_to_lowercase(self):
        req = MediaAnalysisRequest(
            media_hash="A" * 64,
            media_url="https://youtube.com/watch?v=abc",
            platform=Platform.YOUTUBE,
        )
        assert req.media_hash == "a" * 64

    def test_invalid_url_rejected(self):
        with pytest.raises(ValidationError):
            MediaAnalysisRequest(
                media_hash="a" * 64,
                media_url="not-a-url",
                platform=Platform.YOUTUBE,
            )

    def test_invalid_platform_rejected(self):
        with pytest.raises(ValidationError):
            MediaAnalysisRequest(
                media_hash="a" * 64,
                media_url="https://youtube.com/watch?v=abc",
                platform="instagram",
            )

    def test_default_media_type_is_video(self):
        req = MediaAnalysisRequest(
            media_hash="a" * 64,
            media_url="https://youtube.com/watch?v=abc",
            platform=Platform.YOUTUBE,
        )
        assert req.media_type == MediaType.VIDEO


class TestAnalysisOptions:
    """Tests for AnalysisOptions validation."""

    def test_defaults(self):
        opts = AnalysisOptions()
        assert opts.skip_blockchain is False
        assert opts.detailed_report is False
        assert opts.max_frames == 0
        assert opts.confidence_threshold == 0.7

    def test_max_frames_clamped(self):
        with pytest.raises(ValidationError):
            AnalysisOptions(max_frames=500)

    def test_threshold_range(self):
        with pytest.raises(ValidationError):
            AnalysisOptions(confidence_threshold=1.5)


class TestMLResultResponse:
    """Tests for MLResultResponse model."""

    def test_valid_response(self):
        resp = MLResultResponse(is_synthetic=True, confidence=0.95)
        assert resp.is_synthetic is True
        assert resp.model_version == "xception-gru-v1"

    def test_confidence_range(self):
        with pytest.raises(ValidationError):
            MLResultResponse(is_synthetic=False, confidence=1.5)

    def test_defaults(self):
        resp = MLResultResponse(is_synthetic=False, confidence=0.1)
        assert resp.artifacts == []
        assert resp.spatial is None


class TestInputValidators:
    """Tests for input validation utilities."""

    def test_valid_sha256_hashes(self):
        from api.app.utils.validators import is_valid_sha256
        assert is_valid_sha256("a" * 64) is True
        assert is_valid_sha256("0123456789abcdef" * 4) is True

    def test_invalid_sha256_hashes(self):
        from api.app.utils.validators import is_valid_sha256
        assert is_valid_sha256("short") is False
        assert is_valid_sha256("g" * 64) is False
        assert is_valid_sha256("") is False

    def test_valid_eth_address(self):
        from api.app.utils.validators import is_valid_eth_address
        assert is_valid_eth_address("0x" + "A" * 40) is True

    def test_invalid_eth_address(self):
        from api.app.utils.validators import is_valid_eth_address
        assert is_valid_eth_address("0x123") is False
        assert is_valid_eth_address("not_an_address") is False

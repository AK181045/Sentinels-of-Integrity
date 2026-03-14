"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Detection Service
Tests the core detection orchestration logic.
=============================================================================
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from api.app.services.detection_service import DetectionService
from api.app.models.schemas import (
    MLResultResponse,
    BlockchainResultResponse,
    AnalysisOptions,
    SpatialAnalysis,
    TemporalAnalysis,
    FrequencyAnalysis,
)


class TestDetectionService:
    """Tests for DetectionService."""

    @pytest.fixture
    def service(self):
        return DetectionService()

    @pytest.fixture
    def sample_hash(self):
        return "a" * 64  # Valid SHA-256 hex hash

    @pytest.fixture
    def sample_url(self):
        return "https://www.youtube.com/watch?v=test123"

    # =========================================================================
    # Test: Parallel ML + Blockchain execution
    # =========================================================================

    @pytest.mark.asyncio
    async def test_analyze_returns_both_results(self, service, sample_hash, sample_url):
        """Verify that analyze() returns both ML and blockchain results."""
        ml_result, blockchain_result = await service.analyze(
            media_hash=sample_hash,
            media_url=sample_url,
            platform="youtube",
        )

        assert isinstance(ml_result, MLResultResponse)
        assert isinstance(blockchain_result, BlockchainResultResponse)

    @pytest.mark.asyncio
    async def test_analyze_ml_result_has_required_fields(self, service, sample_hash, sample_url):
        """ML result should contain is_synthetic, confidence, and artifacts."""
        ml_result, _ = await service.analyze(
            media_hash=sample_hash,
            media_url=sample_url,
            platform="youtube",
        )

        assert hasattr(ml_result, "is_synthetic")
        assert hasattr(ml_result, "confidence")
        assert hasattr(ml_result, "artifacts")
        assert 0.0 <= ml_result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_analyze_blockchain_result_has_required_fields(self, service, sample_hash, sample_url):
        """Blockchain result should contain is_registered and edit_history."""
        _, blockchain_result = await service.analyze(
            media_hash=sample_hash,
            media_url=sample_url,
            platform="youtube",
        )

        assert hasattr(blockchain_result, "is_registered")
        assert hasattr(blockchain_result, "edit_history")
        assert isinstance(blockchain_result.edit_history, list)

    # =========================================================================
    # Test: Skip blockchain option
    # =========================================================================

    @pytest.mark.asyncio
    async def test_analyze_skip_blockchain(self, service, sample_hash, sample_url):
        """When skip_blockchain=True, blockchain result should be default."""
        options = AnalysisOptions(skip_blockchain=True)
        ml_result, blockchain_result = await service.analyze(
            media_hash=sample_hash,
            media_url=sample_url,
            platform="youtube",
            options=options,
        )

        assert isinstance(ml_result, MLResultResponse)
        assert blockchain_result.is_registered is False
        assert blockchain_result.author is None

    # =========================================================================
    # Test: Graceful degradation
    # =========================================================================

    @pytest.mark.asyncio
    async def test_default_ml_result_on_failure(self, service):
        """When ML inference fails, default result should be returned."""
        default = service._default_ml_result()
        assert default.is_synthetic is False
        assert default.confidence == 0.0
        assert "ml_unavailable" in default.artifacts

    @pytest.mark.asyncio
    async def test_default_blockchain_result_on_failure(self, service):
        """When blockchain lookup fails, default result should be returned."""
        default = service._default_blockchain_result()
        assert default.is_registered is False
        assert default.author is None
        assert default.zk_verified is False

    # =========================================================================
    # Test: Report storage
    # =========================================================================

    @pytest.mark.asyncio
    async def test_store_report_does_not_raise(self, service):
        """Store report should not raise exceptions (background task)."""
        await service.store_report("test-id", {"test": "data"})

    @pytest.mark.asyncio
    async def test_get_report_returns_none_for_unknown(self, service):
        """Get report for unknown ID should return None."""
        result = await service.get_report("nonexistent-id")
        assert result is None


class TestDetectionServiceIntegration:
    """Integration-style tests for DetectionService."""

    @pytest.mark.asyncio
    async def test_full_analysis_flow(self):
        """End-to-end test of the analysis flow."""
        service = DetectionService()
        ml_result, blockchain_result = await service.analyze(
            media_hash="b" * 64,
            media_url="https://www.youtube.com/watch?v=test",
            platform="youtube",
        )

        # Verify complete result structure
        assert ml_result.model_version is not None
        assert isinstance(ml_result.artifacts, list)
        assert isinstance(blockchain_result.edit_history, list)

    @pytest.mark.asyncio
    async def test_analysis_with_all_options(self):
        """Test analysis with all options specified."""
        service = DetectionService()
        options = AnalysisOptions(
            skip_blockchain=False,
            detailed_report=True,
            max_frames=100,
            confidence_threshold=0.8,
        )
        ml_result, blockchain_result = await service.analyze(
            media_hash="c" * 64,
            media_url="https://x.com/user/status/123",
            platform="twitter",
            options=options,
        )

        assert isinstance(ml_result, MLResultResponse)
        assert isinstance(blockchain_result, BlockchainResultResponse)

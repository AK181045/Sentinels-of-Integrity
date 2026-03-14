"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Score Aggregator
Tests the weighted scoring algorithm that produces the Sentinels Score.
=============================================================================
"""

import pytest
from api.app.services.score_aggregator import ScoreAggregator
from api.app.models.schemas import (
    MLResultResponse,
    BlockchainResultResponse,
    SpatialAnalysis,
    TemporalAnalysis,
    FrequencyAnalysis,
    Verdict,
)


class TestScoreAggregator:
    """Tests for ScoreAggregator weighted scoring."""

    @pytest.fixture
    def aggregator(self):
        return ScoreAggregator()

    def _make_ml(self, confidence=0.1, spatial=None, temporal=None, frequency=None):
        return MLResultResponse(
            is_synthetic=confidence > 0.5,
            confidence=confidence,
            artifacts=[],
            model_version="test-v1",
            spatial=spatial,
            temporal=temporal,
            frequency=frequency,
        )

    def _make_blockchain(self, registered=False, zk=False):
        return BlockchainResultResponse(
            is_registered=registered,
            author="0x" + "A" * 40 if registered else None,
            zk_verified=zk,
        )

    # =========================================================================
    # Verdict thresholds
    # =========================================================================

    def test_authentic_verdict_high_trust(self, aggregator):
        """Low ML synthetic confidence → high trust → AUTHENTIC."""
        ml = self._make_ml(confidence=0.05)
        bc = self._make_blockchain(registered=True)
        score, verdict = aggregator.compute_score(ml, bc)
        assert verdict == Verdict.AUTHENTIC.value
        assert score >= 70.0

    def test_synthetic_verdict_high_confidence(self, aggregator):
        """High ML synthetic confidence → low trust → SYNTHETIC."""
        ml = self._make_ml(confidence=0.95)
        bc = self._make_blockchain(registered=False)
        score, verdict = aggregator.compute_score(ml, bc)
        assert verdict == Verdict.SYNTHETIC.value
        assert score < 40.0

    def test_suspicious_verdict_mid_confidence(self, aggregator):
        """Medium ML confidence → SUSPICIOUS."""
        ml = self._make_ml(confidence=0.55)
        bc = self._make_blockchain(registered=False)
        score, verdict = aggregator.compute_score(ml, bc)
        assert verdict == Verdict.SUSPICIOUS.value
        assert 40.0 <= score < 70.0

    # =========================================================================
    # Score range
    # =========================================================================

    def test_score_always_0_to_100(self, aggregator):
        """Score must be clamped to [0, 100]."""
        for conf in [0.0, 0.25, 0.5, 0.75, 1.0]:
            for registered in [True, False]:
                ml = self._make_ml(confidence=conf)
                bc = self._make_blockchain(registered=registered)
                score, _ = aggregator.compute_score(ml, bc)
                assert 0.0 <= score <= 100.0, f"Score {score} out of range for conf={conf}"

    # =========================================================================
    # Blockchain provenance bonus
    # =========================================================================

    def test_blockchain_registration_boosts_score(self, aggregator):
        """Registered content should get a higher score than unregistered."""
        ml = self._make_ml(confidence=0.3)
        score_unreg, _ = aggregator.compute_score(ml, self._make_blockchain(registered=False))
        score_reg, _ = aggregator.compute_score(ml, self._make_blockchain(registered=True))
        assert score_reg > score_unreg

    def test_zk_verification_boosts_above_registration(self, aggregator):
        """ZK verified should score higher than just registered."""
        ml = self._make_ml(confidence=0.3)
        score_reg, _ = aggregator.compute_score(ml, self._make_blockchain(registered=True, zk=False))
        score_zk, _ = aggregator.compute_score(ml, self._make_blockchain(registered=True, zk=True))
        assert score_zk >= score_reg

    # =========================================================================
    # Spatial analysis impact
    # =========================================================================

    def test_good_spatial_improves_score(self, aggregator):
        """High face consistency + low edge artifacts → higher score."""
        spatial_good = SpatialAnalysis(face_consistency_score=0.95, edge_artifact_score=0.05, faces_detected=1)
        spatial_bad = SpatialAnalysis(face_consistency_score=0.2, edge_artifact_score=0.9, faces_detected=1)

        ml_good = self._make_ml(confidence=0.3, spatial=spatial_good)
        ml_bad = self._make_ml(confidence=0.3, spatial=spatial_bad)
        bc = self._make_blockchain()

        score_good, _ = aggregator.compute_score(ml_good, bc)
        score_bad, _ = aggregator.compute_score(ml_bad, bc)
        assert score_good > score_bad

    # =========================================================================
    # Temporal analysis impact
    # =========================================================================

    def test_good_temporal_improves_score(self, aggregator):
        """High temporal consistency → higher score."""
        temporal_good = TemporalAnalysis(temporal_consistency=0.95, frames_analyzed=90, anomaly_frames=[])
        temporal_bad = TemporalAnalysis(temporal_consistency=0.2, frames_analyzed=90, anomaly_frames=[10, 20, 30])

        ml_good = self._make_ml(confidence=0.3, temporal=temporal_good)
        ml_bad = self._make_ml(confidence=0.3, temporal=temporal_bad)
        bc = self._make_blockchain()

        score_good, _ = aggregator.compute_score(ml_good, bc)
        score_bad, _ = aggregator.compute_score(ml_bad, bc)
        assert score_good > score_bad

    # =========================================================================
    # Frequency analysis impact
    # =========================================================================

    def test_ghosting_heavily_penalizes_score(self, aggregator):
        """Ghosting detection should significantly reduce score."""
        freq_clean = FrequencyAnalysis(spectral_anomaly_score=0.05, ghosting_detected=False)
        freq_ghost = FrequencyAnalysis(spectral_anomaly_score=0.5, ghosting_detected=True)

        ml_clean = self._make_ml(confidence=0.3, frequency=freq_clean)
        ml_ghost = self._make_ml(confidence=0.3, frequency=freq_ghost)
        bc = self._make_blockchain()

        score_clean, _ = aggregator.compute_score(ml_clean, bc)
        score_ghost, _ = aggregator.compute_score(ml_ghost, bc)
        assert score_clean > score_ghost

    # =========================================================================
    # Return type validation
    # =========================================================================

    def test_returns_tuple(self, aggregator):
        """compute_score should return (float, str) tuple."""
        score, verdict = aggregator.compute_score(self._make_ml(), self._make_blockchain())
        assert isinstance(score, float)
        assert isinstance(verdict, str)
        assert verdict in [v.value for v in Verdict]

    def test_score_is_rounded(self, aggregator):
        """Score should be rounded to 1 decimal place."""
        score, _ = aggregator.compute_score(self._make_ml(), self._make_blockchain())
        assert score == round(score, 1)

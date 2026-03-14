"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Trust Scorer
Tests the trust score computation logic.
=============================================================================
"""

import pytest
from ml_models.inference.trust_scorer import TrustScorer


class TestTrustScorer:
    """Tests for TrustScorer."""

    @pytest.fixture
    def scorer(self):
        return TrustScorer(confidence_threshold=0.7)

    # =========================================================================
    # Test: Basic scoring
    # =========================================================================

    def test_low_confidence_is_not_synthetic(self, scorer):
        """Low ML confidence should not flag as synthetic."""
        ml_result = {"confidence": 0.2, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.1}

        report = scorer.compute(ml_result, freq_result)
        assert report["is_synthetic"] is False

    def test_high_confidence_is_synthetic(self, scorer):
        """High ML confidence should flag as synthetic."""
        ml_result = {"confidence": 0.95, "artifacts": ["face_warp"]}
        freq_result = {"ghosting_detected": True, "spectral_anomaly_score": 0.8}

        report = scorer.compute(ml_result, freq_result)
        assert report["is_synthetic"] is True

    def test_threshold_boundary(self, scorer):
        """Confidence exactly at threshold should be flagged."""
        ml_result = {"confidence": 0.7, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.1}

        report = scorer.compute(ml_result, freq_result)
        assert report["is_synthetic"] is False  # 0.7 is not > 0.7

    def test_above_threshold(self, scorer):
        """Confidence above threshold should be flagged."""
        ml_result = {"confidence": 0.71, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.1}

        report = scorer.compute(ml_result, freq_result)
        assert report["is_synthetic"] is True

    # =========================================================================
    # Test: Artifact collection
    # =========================================================================

    def test_ghosting_added_to_artifacts(self, scorer):
        """Ghosting detection should add 'ghosting' to artifacts list."""
        ml_result = {"confidence": 0.5, "artifacts": ["face_warp"]}
        freq_result = {"ghosting_detected": True, "spectral_anomaly_score": 0.2}

        report = scorer.compute(ml_result, freq_result)
        assert "ghosting" in report["artifacts"]
        assert "face_warp" in report["artifacts"]

    def test_spectral_anomaly_added(self, scorer):
        """High spectral anomaly should add 'spectral_anomaly' to artifacts."""
        ml_result = {"confidence": 0.3, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.5}

        report = scorer.compute(ml_result, freq_result)
        assert "spectral_anomaly" in report["artifacts"]

    def test_no_artifacts_when_clean(self, scorer):
        """Clean media should have empty artifacts list."""
        ml_result = {"confidence": 0.1, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.1}

        report = scorer.compute(ml_result, freq_result)
        assert report["artifacts"] == []

    # =========================================================================
    # Test: Output structure
    # =========================================================================

    def test_report_has_required_keys(self, scorer):
        """Report should contain all required keys."""
        ml_result = {"confidence": 0.5, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.2}

        report = scorer.compute(ml_result, freq_result)
        required_keys = ["is_synthetic", "confidence", "artifacts", "model_version", "frequency"]
        for key in required_keys:
            assert key in report, f"Missing key: {key}"

    def test_confidence_passthrough(self, scorer):
        """Confidence value should be passed through unchanged."""
        ml_result = {"confidence": 0.42, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.1}

        report = scorer.compute(ml_result, freq_result)
        assert report["confidence"] == 0.42

    def test_model_version_present(self, scorer):
        """Report should include model version string."""
        ml_result = {"confidence": 0.1, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.1}

        report = scorer.compute(ml_result, freq_result)
        assert report["model_version"] == "xception-gru-v1"


class TestTrustScorerCustomThreshold:
    """Tests with custom confidence thresholds."""

    def test_low_threshold(self):
        """Lower threshold should flag more content as synthetic."""
        scorer = TrustScorer(confidence_threshold=0.3)
        ml_result = {"confidence": 0.35, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.1}

        report = scorer.compute(ml_result, freq_result)
        assert report["is_synthetic"] is True

    def test_high_threshold(self):
        """Higher threshold should be more lenient."""
        scorer = TrustScorer(confidence_threshold=0.9)
        ml_result = {"confidence": 0.85, "artifacts": []}
        freq_result = {"ghosting_detected": False, "spectral_anomaly_score": 0.1}

        report = scorer.compute(ml_result, freq_result)
        assert report["is_synthetic"] is False

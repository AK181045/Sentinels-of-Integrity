"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: ML Models
Tests Xception CNN, Temporal GRU, and Ensemble architectures.
=============================================================================
"""

import pytest
import torch
from ml_models.models.xception_cnn import XceptionCNN
from ml_models.models.temporal_gru import TemporalGRU
from ml_models.models.ensemble import EnsembleDetector


class TestXceptionCNN:
    """Tests for XceptionCNN architecture."""

    @pytest.fixture
    def model(self):
        return XceptionCNN(num_classes=2, pretrained=False)

    def test_forward_shape(self, model):
        """Output should be (batch, num_classes)."""
        x = torch.randn(2, 3, 299, 299)
        out = model(x)
        assert out.shape == (2, 2)

    def test_extract_features_shape(self, model):
        """Feature extraction should return (batch, 1024)."""
        x = torch.randn(2, 3, 299, 299)
        features = model.extract_features(x)
        assert features.shape == (2, 1024)

    def test_spatial_scores(self, model):
        """get_spatial_scores should return dict with required keys."""
        x = torch.randn(1, 3, 299, 299)
        scores = model.get_spatial_scores(x)
        assert "is_synthetic" in scores
        assert "confidence" in scores
        assert 0.0 <= scores["confidence"] <= 1.0

    def test_feature_dim_attribute(self, model):
        assert model.feature_dim == 1024


class TestTemporalGRU:
    """Tests for Bi-directional GRU temporal model."""

    @pytest.fixture
    def model(self):
        return TemporalGRU(input_dim=1024, hidden_size=256, num_layers=2, bidirectional=True)

    def test_forward_shape(self, model):
        """Output should be (batch, num_classes)."""
        x = torch.randn(2, 30, 1024)  # (batch, seq_len, features)
        out = model(x)
        assert out.shape == (2, 2)

    def test_temporal_scores(self, model):
        """get_temporal_scores should return dict with temporal metrics."""
        x = torch.randn(1, 30, 1024)
        scores = model.get_temporal_scores(x)
        assert "temporal_consistency" in scores
        assert "frames_analyzed" in scores
        assert "anomaly_frames" in scores
        assert scores["frames_analyzed"] == 30

    def test_bidirectional_feature_dim(self, model):
        assert model.feature_dim == 512  # 256 * 2


class TestEnsembleDetector:
    """Tests for Ensemble model combining CNN + GRU + frequency."""

    @pytest.fixture
    def model(self):
        return EnsembleDetector()

    def test_forward_shape(self, model):
        """Output should be (batch, 2)."""
        frames = torch.randn(1, 10, 3, 299, 299)
        freq = torch.randn(1, 1)
        out = model(frames, freq)
        assert out.shape == (1, 2)

    def test_predict_output(self, model):
        """predict should return dict with is_synthetic and confidence."""
        frames = torch.randn(1, 10, 3, 299, 299)
        freq = torch.randn(1, 1)
        result = model.predict(frames, freq)
        assert "is_synthetic" in result
        assert "confidence" in result
        assert isinstance(result["is_synthetic"], bool)
        assert 0.0 <= result["confidence"] <= 1.0

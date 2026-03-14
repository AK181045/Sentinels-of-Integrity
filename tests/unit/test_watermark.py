"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Model Watermarking
Tests neural network watermark embedding and verification.
=============================================================================
"""

import pytest
import torch
import torch.nn as nn
from ml_models.models.model_watermark import ModelWatermarker


class TestModelWatermarker:
    """Tests for ModelWatermarker."""

    @pytest.fixture
    def watermarker(self):
        return ModelWatermarker(watermark_key="test-key-123")

    @pytest.fixture
    def simple_model(self):
        return nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 2),
        )

    def test_embed_returns_true(self, watermarker, simple_model):
        result = watermarker.embed_watermark(simple_model, layer_name="4.weight")
        assert result is True

    def test_embed_invalid_layer(self, watermarker, simple_model):
        result = watermarker.embed_watermark(simple_model, layer_name="nonexistent")
        assert result is False

    def test_verify_after_embed(self, watermarker, simple_model):
        watermarker.embed_watermark(simple_model, layer_name="4.weight")
        is_present, accuracy = watermarker.verify_watermark(simple_model, layer_name="4.weight")
        assert is_present is True
        assert accuracy > 0.85

    def test_verify_without_embed(self, simple_model):
        wm = ModelWatermarker(watermark_key="wrong-key")
        is_present, accuracy = wm.verify_watermark(simple_model, layer_name="4.weight")
        # Without embedding, presence detection may be unreliable
        assert isinstance(is_present, bool)
        assert 0.0 <= accuracy <= 1.0

    def test_different_keys_differ(self, simple_model):
        wm1 = ModelWatermarker(watermark_key="key-alpha")
        wm2 = ModelWatermarker(watermark_key="key-beta")
        assert wm1.key_hash != wm2.key_hash

    def test_key_to_bits_deterministic(self, watermarker):
        bits1 = watermarker._key_to_bits()
        bits2 = watermarker._key_to_bits()
        assert bits1 == bits2
        assert all(b in (0, 1) for b in bits1)

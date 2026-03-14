"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Steganography
Tests DCT-domain watermark embedding and extraction.
=============================================================================
"""

import pytest
import numpy as np
from contracts.watermark.steganography import DCTSteganography


class TestDCTSteganography:
    """Tests for DCT-domain steganography."""

    @pytest.fixture
    def stego(self):
        return DCTSteganography(strength=25.0, block_size=8)

    @pytest.fixture
    def sample_frame(self):
        return np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)

    def test_embed_returns_same_shape(self, stego, sample_frame):
        result = stego.embed(sample_frame, "test")
        assert result.shape == sample_frame.shape
        assert result.dtype == sample_frame.dtype

    def test_embed_extract_roundtrip(self, stego, sample_frame):
        payload = "SOI"
        embedded = stego.embed(sample_frame, payload)
        extracted = stego.extract(embedded, len(payload))
        assert extracted == payload

    def test_different_payloads(self, stego, sample_frame):
        embedded_a = stego.embed(sample_frame.copy(), "AAA")
        embedded_b = stego.embed(sample_frame.copy(), "BBB")
        # Different payloads should produce different frames
        assert not np.array_equal(embedded_a, embedded_b)

    def test_grayscale_frame(self, stego):
        gray = np.random.randint(50, 200, (256, 256), dtype=np.uint8)
        payload = "Hi"
        embedded = stego.embed(gray, payload)
        extracted = stego.extract(embedded, len(payload))
        assert extracted == payload

    def test_text_to_bits_roundtrip(self, stego):
        text = "abc"
        bits = stego._text_to_bits(text)
        recovered = stego._bits_to_text(bits)
        assert recovered == text

    def test_bits_length(self, stego):
        bits = stego._text_to_bits("A")
        assert len(bits) == 8  # 1 ASCII char = 8 bits

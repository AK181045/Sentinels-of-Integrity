"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Frequency Analyzer
Tests FFT/DCT frequency domain analysis for ghosting detection.
=============================================================================
"""

import pytest
import numpy as np
from ml_models.preprocessing.frequency_analyzer import FrequencyAnalyzer


class TestFrequencyAnalyzer:
    """Tests for FrequencyAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        return FrequencyAnalyzer(high_freq_threshold=0.3)

    @pytest.fixture
    def clean_frame(self):
        """Create a smooth, naturally-looking frame (low high-freq energy)."""
        frame = np.zeros((299, 299, 3), dtype=np.uint8)
        # Smooth gradient — low high-frequency content
        for i in range(299):
            frame[i, :, :] = int(255 * i / 299)
        return frame

    @pytest.fixture
    def noisy_frame(self):
        """Create a high-frequency noise frame (suspicious)."""
        return np.random.randint(0, 255, (299, 299, 3), dtype=np.uint8)

    # =========================================================================
    # FFT computation
    # =========================================================================

    def test_fft_returns_2d_array(self, analyzer, clean_frame):
        spectrum = analyzer.compute_fft(clean_frame)
        assert isinstance(spectrum, np.ndarray)
        assert len(spectrum.shape) == 2

    def test_fft_shape_matches_input(self, analyzer, clean_frame):
        spectrum = analyzer.compute_fft(clean_frame)
        assert spectrum.shape == (299, 299)

    # =========================================================================
    # DCT computation
    # =========================================================================

    def test_dct_returns_2d_array(self, analyzer, clean_frame):
        dct = analyzer.compute_dct(clean_frame)
        assert isinstance(dct, np.ndarray)
        assert len(dct.shape) == 2

    # =========================================================================
    # Ghosting detection
    # =========================================================================

    def test_clean_frame_no_ghosting(self, analyzer, clean_frame):
        ghosting, score = analyzer.detect_ghosting(clean_frame)
        assert isinstance(ghosting, bool)
        assert isinstance(score, float)

    def test_noisy_frame_higher_anomaly(self, analyzer, clean_frame, noisy_frame):
        _, clean_score = analyzer.detect_ghosting(clean_frame)
        _, noisy_score = analyzer.detect_ghosting(noisy_frame)
        # Noisy frames should have higher anomaly scores
        assert noisy_score > clean_score

    # =========================================================================
    # Frame analysis
    # =========================================================================

    def test_analyze_frame_returns_dict(self, analyzer, clean_frame):
        result = analyzer.analyze_frame(clean_frame)
        assert "spectral_anomaly_score" in result
        assert "ghosting_detected" in result
        assert 0.0 <= result["spectral_anomaly_score"] <= 1.0

    # =========================================================================
    # Video analysis
    # =========================================================================

    def test_analyze_video_aggregates(self, analyzer, clean_frame):
        frames = np.array([clean_frame] * 5)
        result = analyzer.analyze_video(frames)
        assert "spectral_anomaly_score" in result
        assert "ghosting_detected" in result
        assert "ghosting_frame_ratio" in result
        assert 0.0 <= result["ghosting_frame_ratio"] <= 1.0

"""
SENTINELS OF INTEGRITY — Frequency Domain Analyzer
FFT/DCT analysis for spectral ghosting detection.
(PRD.txt §2: "Spatial/Frequency analysis to detect ghosting")
"""

import numpy as np
import cv2
import logging

logger = logging.getLogger("sentinels.ml.preprocessing.frequency")


class FrequencyAnalyzer:
    """Analyzes frames in the frequency domain to detect synthesis artifacts."""

    def __init__(self, high_freq_threshold: float = 0.3):
        self.high_freq_threshold = high_freq_threshold

    def compute_fft(self, frame: np.ndarray) -> np.ndarray:
        """Compute 2D FFT magnitude spectrum of a grayscale frame."""
        if len(frame.shape) == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        f_transform = np.fft.fft2(frame.astype(np.float32))
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.log1p(np.abs(f_shift))
        return magnitude

    def compute_dct(self, frame: np.ndarray) -> np.ndarray:
        """Compute 2D DCT (Discrete Cosine Transform)."""
        if len(frame.shape) == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        return cv2.dct(frame.astype(np.float32))

    def detect_ghosting(self, frame: np.ndarray) -> tuple[bool, float]:
        """Detect spectral ghosting artifacts. Returns (detected, score)."""
        spectrum = self.compute_fft(frame)
        h, w = spectrum.shape
        center_y, center_x = h // 2, w // 2

        # Analyze high-frequency energy distribution
        radius = min(h, w) // 4
        high_freq_mask = np.ones((h, w), dtype=bool)
        y, x = np.ogrid[:h, :w]
        high_freq_mask[(y - center_y)**2 + (x - center_x)**2 <= radius**2] = False

        high_energy = np.mean(spectrum[high_freq_mask])
        total_energy = np.mean(spectrum)
        ratio = high_energy / (total_energy + 1e-8)

        ghosting = ratio > self.high_freq_threshold
        return ghosting, float(ratio)

    def analyze_frame(self, frame: np.ndarray) -> dict:
        """Full frequency analysis of a single frame."""
        ghosting_detected, anomaly_score = self.detect_ghosting(frame)
        return {
            "spectral_anomaly_score": min(1.0, anomaly_score),
            "ghosting_detected": ghosting_detected,
        }

    def analyze_video(self, frames: np.ndarray) -> dict:
        """Aggregate frequency analysis across all frames."""
        scores = [self.analyze_frame(f) for f in frames]
        avg_anomaly = np.mean([s["spectral_anomaly_score"] for s in scores])
        ghosting_count = sum(1 for s in scores if s["ghosting_detected"])
        return {
            "spectral_anomaly_score": float(avg_anomaly),
            "ghosting_detected": ghosting_count > len(frames) * 0.3,
            "ghosting_frame_ratio": ghosting_count / max(len(frames), 1),
        }

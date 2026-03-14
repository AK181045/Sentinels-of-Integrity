"""
SENTINELS OF INTEGRITY — Watermark Extractor
Extracts and verifies steganographic watermarks.
"""

import numpy as np
import logging
from contracts.watermark.steganography import DCTSteganography

logger = logging.getLogger("sentinels.watermark.extractor")


class WatermarkExtractor:
    """Extracts steganographic watermarks from frames."""

    def __init__(self, strength: float = 25.0):
        self.stego = DCTSteganography(strength=strength)

    def extract_from_frame(self, frame: np.ndarray, payload_length: int) -> str:
        """Extract watermark from a single frame."""
        return self.stego.extract(frame, payload_length)

    def extract_from_video(self, frames: list[np.ndarray], payload_length: int, interval: int = 5) -> tuple[str, float]:
        """Extract from multiple frames and vote on the result."""
        extractions = []
        for i, frame in enumerate(frames):
            if i % interval == 0:
                try:
                    payload = self.stego.extract(frame, payload_length)
                    extractions.append(payload)
                except Exception:
                    pass

        if not extractions:
            return "", 0.0

        # Majority voting
        from collections import Counter
        counter = Counter(extractions)
        best, count = counter.most_common(1)[0]
        confidence = count / len(extractions)
        logger.info(f"Extracted watermark with {confidence:.0%} confidence")
        return best, confidence

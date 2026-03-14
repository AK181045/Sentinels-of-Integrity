"""
SENTINELS OF INTEGRITY — Steganographic Watermark Embedder
Embeds invisible watermarks that survive compression and re-encoding.
(PRD.txt §3B: "steganographic watermarking that survives compression")
"""

import numpy as np
import cv2
import logging
from contracts.watermark.steganography import DCTSteganography

logger = logging.getLogger("sentinels.watermark.embedder")


class WatermarkEmbedder:
    """Embeds steganographic watermarks into video frames."""

    def __init__(self, strength: float = 25.0):
        self.stego = DCTSteganography(strength=strength)

    def embed_in_frame(self, frame: np.ndarray, payload: str) -> np.ndarray:
        """Embed watermark payload into a single frame."""
        return self.stego.embed(frame, payload)

    def embed_in_video(self, frames: list[np.ndarray], payload: str, interval: int = 5) -> list[np.ndarray]:
        """Embed watermark in every Nth frame for redundancy."""
        watermarked = []
        for i, frame in enumerate(frames):
            if i % interval == 0:
                watermarked.append(self.stego.embed(frame, payload))
            else:
                watermarked.append(frame)
        logger.info(f"Watermarked {len(frames)//interval} of {len(frames)} frames")
        return watermarked
